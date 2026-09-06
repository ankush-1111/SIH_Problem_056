from .base import IndexStrategy
from typing import List
from ..models import RepresentativeFare, Route, BasePeriod

class LaspeyresStrategy(IndexStrategy):
    def calculate(self, fares: List[RepresentativeFare], routes: List[Route], base_periods: List[BasePeriod]) -> float:
        route_weights = {r.id: r.weight for r in routes}
        base_fares = {(b.route_id, b.booking_window): b.base_fare for b in base_periods}

        weighted_current_sum = 0.0
        weighted_base_sum = 0.0

        for fare in fares:
            weight = route_weights.get(fare.route_id, 0)
            base_fare = base_fares.get((fare.route_id, fare.booking_window), 0)
            if weight > 0 and base_fare > 0:
                weighted_current_sum += (fare.fare * weight)
                weighted_base_sum += (base_fare * weight)

        if weighted_base_sum == 0:
            return 0.0

        return (weighted_current_sum / weighted_base_sum) * 100
