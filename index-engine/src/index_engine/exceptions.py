class IndexEngineError(Exception):
    pass

class DatabaseError(IndexEngineError):
    pass

class CalculationError(IndexEngineError):
    pass
