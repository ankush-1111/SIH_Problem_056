from abc import ABC, abstractmethod
from typing import List
from ..models import RepresentativeFare, Route, BasePeriod

class IndexStrategy(ABC):
    @abstractmethod
    def calculate(self, fares: List[RepresentativeFare], routes: List[Route], base_periods: List[BasePeriod]) -> float:
        pass
