from .base import IndexStrategy
from typing import List
from collections import defaultdict
from ..models import RepresentativeFare, Route, BasePeriod

class LaspeyresStrategy(IndexStrategy):
    def calculate(self, fares: List[RepresentativeFare], routes: List[Route], base_periods: List[BasePeriod]) -> float:
        """Compute the Laspeyres Price Index (APIx).

        Formula:
            APIx = (Σ [w_r * P_r^t] / Σ [w_r * P_r^0]) * 100

        where:
            w_r   = Statistical weight of route r (normalized, Σ w_r ≈ 1.0)
            P_r^t = Representative fare for route r in current period t (mean across observed booking windows)
            P_r^0 = Base period representative fare for route r (Jan 2026 baseline across matched booking windows)

        Properties:
            - Dimensionless index value (no currency units).
            - Base period: January 2026 = 100.
            - If current fares equal base fares: APIx = 100.0.
            - If current fares are 10% higher than base: APIx = 110.0.
        """
        route_weights = {r.id: r.weight for r in routes}
        base_fares = {(b.route_id, b.booking_window): b.base_fare for b in base_periods}

        # Group matched current and base fares by route
        route_current_fares = defaultdict(list)
        route_base_fares = defaultdict(list)

        for fare in fares:
            weight = route_weights.get(fare.route_id, 0)
            base_fare = base_fares.get((fare.route_id, fare.booking_window), 0)
            if weight > 0 and base_fare > 0 and fare.fare > 0:
                route_current_fares[fare.route_id].append(fare.fare)
                route_base_fares[fare.route_id].append(base_fare)

        weighted_current_sum = 0.0
        weighted_base_sum = 0.0

        for route_id, cur_list in route_current_fares.items():
            base_list = route_base_fares[route_id]
            weight = route_weights[route_id]
            avg_current = sum(cur_list) / len(cur_list)
            avg_base = sum(base_list) / len(base_list)
            weighted_current_sum += (avg_current * weight)
            weighted_base_sum += (avg_base * weight)

        if weighted_base_sum == 0:
            return 0.0

        return (weighted_current_sum / weighted_base_sum) * 100

