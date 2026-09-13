from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .repository import Repository
from .calculator import Calculator
from .models import AirfareIndex

class IndexService:
    def __init__(self, repository: Repository, calculator: Calculator):
        self.repository = repository
        self.calculator = calculator

    def run_daily_pipeline(self, target_date: str) -> Optional[float]:
        """Compute the daily APIx for target_date and store it."""
        fares = self.repository.fetch_representative_fares(target_date)
        if not fares:
            return None

        routes = self.repository.fetch_route_weights()
        base_period = self.repository.fetch_base_period()

        daily_index = self.calculator.calculate_daily(fares, routes, base_period)
        if daily_index <= 0:
            return None

        rounded_daily = round(daily_index, 2)
        index = AirfareIndex(date=datetime.strptime(target_date, "%Y-%m-%d").date(), daily_index=rounded_daily)
        self.repository.save_index(index, "daily")
        return rounded_daily

    def run_weekly_pipeline(self, target_date: str, current_daily: Optional[float] = None) -> Optional[float]:
        """Compute the weekly APIx as a 7-day rolling average of daily indices."""
        dt = datetime.strptime(target_date, "%Y-%m-%d").date()
        start_date = (dt - timedelta(days=6)).strftime("%Y-%m-%d")

        daily_values = self.repository.fetch_daily_indices(start_date, target_date)
        if not daily_values and current_daily is not None:
            daily_values = [current_daily]

        if not daily_values:
            return None

        weekly_index = round(self.calculator.calculate_average(daily_values), 2)
        index = AirfareIndex(date=dt, weekly_index=weekly_index)
        self.repository.save_index(index, "weekly")
        return weekly_index

    def run_monthly_pipeline(self, target_date: str, current_daily: Optional[float] = None) -> Optional[float]:
        """Compute the monthly APIx as a 30-day rolling average of daily indices."""
        dt = datetime.strptime(target_date, "%Y-%m-%d").date()
        start_date = (dt - timedelta(days=29)).strftime("%Y-%m-%d")

        daily_values = self.repository.fetch_daily_indices(start_date, target_date)
        if not daily_values and current_daily is not None:
            daily_values = [current_daily]

        if not daily_values:
            return None

        monthly_index = round(self.calculator.calculate_average(daily_values), 2)
        index = AirfareIndex(date=dt, monthly_index=monthly_index)
        self.repository.save_index(index, "monthly")
        return monthly_index

    def run_full_pipeline(self, target_date: str) -> Dict[str, Optional[float]]:
        """Run daily, weekly, and monthly pipelines in sequence for a given date."""
        daily = self.run_daily_pipeline(target_date)
        weekly = self.run_weekly_pipeline(target_date, current_daily=daily)
        monthly = self.run_monthly_pipeline(target_date, current_daily=daily)
        return {"daily": daily, "weekly": weekly, "monthly": monthly}

    def run_all_historical_dates(self) -> List[Dict[str, any]]:
        """Run the full index pipeline chronologically across all available dates in representativefares."""
        dates = self.repository.fetch_all_fare_dates()
        results = []
        for d in dates:
            res = self.run_full_pipeline(d)
            results.append({"date": d, **res})
        return results

