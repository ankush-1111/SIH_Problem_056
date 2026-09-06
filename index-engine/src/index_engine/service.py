from datetime import datetime, timedelta
from .repository import Repository
from .calculator import Calculator
from .models import AirfareIndex

class IndexService:
    def __init__(self, repository: Repository, calculator: Calculator):
        self.repository = repository
        self.calculator = calculator

    def run_daily_pipeline(self, target_date: str):
        """Compute the daily APIx for target_date and store it."""
        fares = self.repository.fetch_representative_fares(target_date)
        routes = self.repository.fetch_route_weights()
        base_period = self.repository.fetch_base_period()

        daily_index = self.calculator.calculate_daily(fares, routes, base_period)

        index = AirfareIndex(date=datetime.strptime(target_date, "%Y-%m-%d").date(), daily_index=round(daily_index, 2))
        self.repository.save_index(index, "daily")
        return daily_index

    def run_weekly_pipeline(self, target_date: str):
        """Compute the weekly APIx as a 7-day rolling average of daily indices."""
        dt = datetime.strptime(target_date, "%Y-%m-%d").date()
        start_date = (dt - timedelta(days=6)).strftime("%Y-%m-%d")

        daily_values = self.repository.fetch_daily_indices(start_date, target_date)
        weekly_index = self.calculator.calculate_average(daily_values)

        index = AirfareIndex(date=dt, weekly_index=round(weekly_index, 2))
        self.repository.save_index(index, "weekly")
        return weekly_index

    def run_monthly_pipeline(self, target_date: str):
        """Compute the monthly APIx as a 30-day rolling average of daily indices."""
        dt = datetime.strptime(target_date, "%Y-%m-%d").date()
        start_date = (dt - timedelta(days=29)).strftime("%Y-%m-%d")

        daily_values = self.repository.fetch_daily_indices(start_date, target_date)
        monthly_index = self.calculator.calculate_average(daily_values)

        index = AirfareIndex(date=dt, monthly_index=round(monthly_index, 2))
        self.repository.save_index(index, "monthly")
        return monthly_index

    def run_full_pipeline(self, target_date: str):
        """Run daily, weekly, and monthly pipelines in sequence for a given date."""
        daily = self.run_daily_pipeline(target_date)
        weekly = self.run_weekly_pipeline(target_date)
        monthly = self.run_monthly_pipeline(target_date)
        return {"daily": daily, "weekly": weekly, "monthly": monthly}
