from dataclasses import dataclass
from datetime import date

@dataclass
class RepresentativeFare:
    route_id: str
    booking_window: str
    date: date
    fare: float

@dataclass
class Route:
    id: str
    weight: float

@dataclass
class BasePeriod:
    route_id: str
    booking_window: str
    base_fare: float

@dataclass
class AirfareIndex:
    date: date
    daily_index: float = 0.0
    weekly_index: float = 0.0
    monthly_index: float = 0.0
    methodology: str = "Laspeyres"
