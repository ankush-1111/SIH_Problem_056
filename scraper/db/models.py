"""Persistent fare and job-audit models."""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Session, relationship
from sqlalchemy.exc import NoResultFound

from scraper.db.database import Base
from scraper.models.fare_quote import FareQuote
from scraper.core.logger import get_logger

logger = get_logger("db")


class Airline(Base):
    __tablename__ = "airlines"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    observations = relationship("FareObservation", back_populates="airline_ref")


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    weight = Column(Numeric(10, 4))

    __table_args__ = (UniqueConstraint("origin", "destination"),)
    observations = relationship("FareObservation", back_populates="route_ref")


class FareObservation(Base):
    __tablename__ = "fare_observations"

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False, index=True)
    origin = Column(String(3), nullable=False, index=True)
    destination = Column(String(3), nullable=False, index=True)
    travel_date = Column(Date, nullable=False, index=True)
    observation_timestamp = Column(DateTime(timezone=True), nullable=False)
    advance_days = Column(Integer, nullable=False, index=True)
    airline = Column(String, nullable=False)
    flight_number = Column(String, nullable=True)
    fare_class = Column(String, nullable=False)
    cabin = Column(String, nullable=False)
    fare_family = Column(String, nullable=True)
    stops = Column(Integer, nullable=False, default=0)
    departure_time = Column(String, nullable=True)
    arrival_time = Column(String, nullable=True)
    base_fare = Column(Numeric(12, 2), nullable=False)
    taxes = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    other_charges = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    total_fare = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="INR")
    availability = Column(String, nullable=False, default="available")
    search_profile = Column(String, nullable=False, default="one_way_economy_1pax")

    # Added columns for unification
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=True)
    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=True)

    route_ref = relationship("Route", back_populates="observations")
    airline_ref = relationship("Airline", back_populates="observations")

    __table_args__ = (
        UniqueConstraint(
            "source", "origin", "destination", "travel_date", "advance_days",
            name="uq_observation_key",
        ),
    )


def get_or_create_route(session, origin, destination):
    route = session.query(Route).filter_by(origin=origin, destination=destination).first()
    if not route:
        route = Route(origin=origin, destination=destination)
        session.add(route)
        session.flush()  # To get the ID
    return route


def get_or_create_airline(session, name):
    airline = session.query(Airline).filter_by(name=name).first()
    if not airline:
        airline = Airline(name=name)
        session.add(airline)
        session.flush()  # To get the ID
    return airline


class JobAudit(Base):
    __tablename__ = "job_audits"

    id = Column(Integer, primary_key=True)
    run_id = Column(String(36), nullable=False, index=True)
    source = Column(String, nullable=False, index=True)
    origin = Column(String(3), nullable=False)
    destination = Column(String(3), nullable=False)
    travel_date = Column(Date, nullable=False)
    advance_days = Column(Integer, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False)
    error_message = Column(String, nullable=True)


def get_existing_observation(session: Session, quote: FareQuote) -> FareObservation | None:
    return (
        session.query(FareObservation)
        .filter_by(
            source=quote.source,
            origin=quote.origin,
            destination=quote.destination,
            travel_date=quote.travel_date,
            advance_days=quote.advance_days,
        )
        .first()
    )


def save_fare_quote(session: Session, quote: FareQuote) -> bool:
    """Insert once per source/route/travel-date/advance-window."""
    if get_existing_observation(session, quote) is not None:
        logger.info(
            f"Duplicate observation skipped: {quote.source} "
            f"{quote.origin}->{quote.destination} T-{quote.advance_days}"
        )
        return False

    # Resolve route and airline
    route = get_or_create_route(session, quote.origin, quote.destination)
    airline = get_or_create_airline(session, quote.airline)

    row = FareObservation(
        **quote.model_dump(),
        route_id=route.id,
        airline_id=airline.id
    )
    session.add(row)
    session.commit()
    logger.info(
        f"Saved: {quote.source} {quote.origin}->{quote.destination} "
        f"T-{quote.advance_days} = {quote.total_fare} {quote.currency} "
        f"(Route ID: {route.id}, Airline ID: {airline.id})"
    )
    return True


def record_job_audit(
    session: Session,
    *,
    run_id: str,
    source: str,
    origin: str,
    destination: str,
    travel_date,
    advance_days: int,
    started_at: datetime,
    status: str,
    finished_at: datetime | None = None,
    error_message: str | None = None,
) -> None:
    session.add(
        JobAudit(
            run_id=run_id,
            source=source,
            origin=origin,
            destination=destination,
            travel_date=travel_date,
            advance_days=advance_days,
            started_at=started_at,
            finished_at=finished_at or datetime.now(timezone.utc),
            status=status,
            error_message=error_message,
        )
    )
    session.commit()
