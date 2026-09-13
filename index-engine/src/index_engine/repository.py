import psycopg2
from typing import List
from .models import RepresentativeFare, Route, BasePeriod, AirfareIndex
from .exceptions import DatabaseError

class Repository:
    def __init__(self, db_url: str):
        self.db_url = db_url

    def _get_connection(self):
        try:
            return psycopg2.connect(self.db_url)
        except psycopg2.Error as e:
            raise DatabaseError(f"Database connection failed: {e}")

    def fetch_representative_fares(self, target_date: str) -> List[RepresentativeFare]:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT route_id, booking_window, date, median_fare FROM representativefares WHERE date = %s", (target_date,))
                rows = cur.fetchall()
                return [RepresentativeFare(r[0], r[1], r[2], float(r[3])) for r in rows]
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to fetch fares: {e}")
        finally:
            conn.close()

    def fetch_route_weights(self) -> List[Route]:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, weight FROM routes")
                rows = cur.fetchall()
                return [Route(r[0], float(r[1]) if r[1] is not None else 0.0) for r in rows]
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to fetch routes: {e}")
        finally:
            conn.close()

    def fetch_base_period(self) -> List[BasePeriod]:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT route_id, booking_window, base_fare FROM baseperiods")
                rows = cur.fetchall()
                return [BasePeriod(r[0], r[1], float(r[2])) for r in rows]
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to fetch base period: {e}")
        finally:
            conn.close()

    def fetch_all_fare_dates(self) -> List[str]:
        """Fetch all distinct dates from representativefares ordered chronologically."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT date FROM representativefares ORDER BY date")
                rows = cur.fetchall()
                return [r[0].strftime("%Y-%m-%d") if hasattr(r[0], "strftime") else str(r[0]) for r in rows]
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to fetch fare dates: {e}")
        finally:
            conn.close()

    def fetch_daily_indices(self, start_date: str, end_date: str) -> list:
        """Fetch daily index values between start_date and end_date (inclusive)."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT daily_index FROM airfareindices WHERE date >= %s AND date <= %s AND daily_index IS NOT NULL AND daily_index > 0 ORDER BY date",
                    (start_date, end_date)
                )
                rows = cur.fetchall()
                return [float(r[0]) for r in rows]
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to fetch daily indices: {e}")
        finally:
            conn.close()

    def save_index(self, index: AirfareIndex, index_type: str):
        """Insert or update an index value for a given date.

        If a row for that date already exists, updates the specific index column.
        Otherwise, inserts a new row.
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                # Check if a row for this date already exists
                cur.execute("SELECT id FROM airfareindices WHERE date = %s LIMIT 1", (index.date,))
                existing = cur.fetchone()

                value = getattr(index, f"{index_type}_index")
                if existing:
                    query = f"UPDATE airfareindices SET {index_type}_index = %s WHERE id = %s"
                    cur.execute(query, (value, existing[0]))
                else:
                    query = f"INSERT INTO airfareindices (date, {index_type}_index) VALUES (%s, %s)"
                    cur.execute(query, (index.date, value))
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise DatabaseError(f"Failed to save {index_type} index: {e}")
        finally:
            conn.close()
