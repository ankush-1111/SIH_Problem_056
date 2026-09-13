from typing import List
from .models import RepresentativeFare, Route, BasePeriod
from .strategies.base import IndexStrategy

class Calculator:
    def __init__(self, strategy: IndexStrategy):
        self.strategy = strategy

    def calculate_daily(self, fares: List[RepresentativeFare], routes: List[Route], base_periods: List[BasePeriod]) -> float:
        return self.strategy.calculate(fares, routes, base_periods)

    def calculate_average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)
