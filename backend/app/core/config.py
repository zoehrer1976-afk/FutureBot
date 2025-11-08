"""
Application Configuration Management
Loads and validates settings from environment variables.
"""

from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Main application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Environment
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "FutureBot"
    VERSION: str = "0.1.0"

    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = Field(..., description="SQLAlchemy database URL")

    # Bybit API
    BYBIT_API_KEY: str = Field(..., min_length=10)
    BYBIT_API_SECRET: str = Field(..., min_length=10)
    BYBIT_TESTNET: bool = True
    BYBIT_BASE_URL: str = "https://api-testnet.bybit.com"

    @field_validator("BYBIT_BASE_URL")
    @classmethod
    def set_bybit_url(cls, v: str, info) -> str:
        """Automatically set Bybit URL based on testnet flag."""
        testnet = info.data.get("BYBIT_TESTNET", True)
        if testnet:
            return "https://api-testnet.bybit.com"
        return "https://api.bybit.com"

    # Trading Configuration
    MAX_POSITION_SIZE_USD: float = Field(1000.0, gt=0)
    MAX_LEVERAGE: int = Field(10, ge=1, le=125)
    RISK_PER_TRADE: float = Field(0.02, gt=0, le=0.1)
    MAX_OPEN_POSITIONS: int = Field(3, ge=1, le=10)
    ENABLE_PAPER_TRADING: bool = True

    # Risk Management
    MAX_DAILY_DRAWDOWN: float = Field(0.05, gt=0, le=0.5)
    MAX_WEEKLY_DRAWDOWN: float = Field(0.10, gt=0, le=0.5)
    CIRCUIT_BREAKER_THRESHOLD: float = Field(0.15, gt=0, le=1.0)
    STOP_LOSS_PERCENTAGE: float = Field(0.02, gt=0, le=0.5)
    TAKE_PROFIT_PERCENTAGE: float = Field(0.04, gt=0, le=1.0)

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FILE: str = "logs/futurebot.log"

    # Feature Flags
    ENABLE_ML_PREDICTIONS: bool = False
    ENABLE_AUTO_TRADING: bool = False
    ENABLE_TELEGRAM_NOTIFICATIONS: bool = False

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"

    def is_testnet(self) -> bool:
        """Check if using Bybit testnet."""
        return self.BYBIT_TESTNET


# Global settings instance
settings = Settings()
