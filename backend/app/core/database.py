"""
Database Connection and Session Management
Async SQLAlchemy setup with connection pooling.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool, StaticPool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


# Database engine configuration
if "sqlite" in settings.DATABASE_URL:
    # SQLite: Use StaticPool for testing, disable pooling
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
else:
    # PostgreSQL/MySQL: Use connection pooling
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get database sessions.

    Yields:
        AsyncSession: Database session

    Example:
        >>> @router.get("/items")
        >>> async def get_items(db: AsyncSession = Depends(get_db)):
        >>>     return await db.execute(select(Item))
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("database_error", error=str(e), exc_info=True)
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database - create all tables.

    Called on application startup.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("database_initialized", url=settings.DATABASE_URL.split("@")[-1])
    except Exception as e:
        logger.error("database_init_failed", error=str(e), exc_info=True)
        raise


async def close_db() -> None:
    """
    Close database connections.

    Called on application shutdown.
    """
    await engine.dispose()
    logger.info("database_connections_closed")
