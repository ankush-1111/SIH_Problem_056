import os
from dataclasses import dataclass

@dataclass
class Config:
    DB_URL: str = os.getenv("DATABASE_URL")
    if not DB_URL:
        raise ValueError("DATABASE_URL must be set in environment")
    BASE_YEAR: int = int(os.getenv("BASE_YEAR", "2026"))
    BASE_MONTH: int = int(os.getenv("BASE_MONTH", "9"))
    METHODOLOGY: str = os.getenv("METHODOLOGY", "Laspeyres")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DECIMAL_PRECISION: int = int(os.getenv("DECIMAL_PRECISION", "2"))
    SUPPORTED_BOOKING_WINDOWS: list = os.getenv("SUPPORTED_BOOKING_WINDOWS", "T+7,T+15,T+30").split(",")
