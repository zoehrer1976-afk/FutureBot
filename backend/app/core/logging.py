"""
Structured Logging Configuration
Uses structlog for structured, machine-readable logs.
"""

import logging
import sys
from pathlib import Path
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from app.core.config import settings


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add application context to log events."""
    event_dict["app"] = settings.PROJECT_NAME
    event_dict["version"] = settings.VERSION
    event_dict["environment"] = settings.ENVIRONMENT
    return event_dict


def setup_logging() -> None:
    """
    Configure structured logging for the application.

    Sets up both standard library logging and structlog with:
    - JSON formatting for production
    - Pretty console output for development
    - File and console handlers
    """
    # Create logs directory if it doesn't exist
    log_file = Path(settings.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL),
    )

    # File handler for persistent logs
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    logging.root.addHandler(file_handler)

    # Shared processors for all configurations
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        add_app_context,
    ]

    # Development: pretty console output
    if settings.ENVIRONMENT == "development":
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    # Production: JSON output for log aggregation
    else:
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Configured structlog logger

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("trade_executed", symbol="BTCUSDT", price=45000)
    """
    return structlog.get_logger(name)


# Initialize logging on module import
setup_logging()
