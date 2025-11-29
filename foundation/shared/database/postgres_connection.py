"""
PostgreSQL database connection and connection pool management using psycopg3
"""

import os
from contextlib import contextmanager
from typing import Generator, Optional
from loguru import logger

try:
    import psycopg
    from psycopg_pool import ConnectionPool

    PSYCOPG3_AVAILABLE = True
    POOL_AVAILABLE = True
except ImportError:
    PSYCOPG3_AVAILABLE = False
    POOL_AVAILABLE = False
    psycopg = None
    ConnectionPool = None
    logger.warning("psycopg3 is required. Install with: pip install 'psycopg[binary] psycopg_pool'")

from shared.config.settings import settings

# Set encoding for Windows compatibility
os.environ.setdefault("PGCLIENTENCODING", "UTF8")


class PostgreSQLConnectionPool:
    """
    PostgreSQL connection pool manager using psycopg3.

    Implements connection pooling for efficient database connection management.
    Reuses connections to reduce overhead and improve performance under load.
    """

    _pool: Optional[ConnectionPool] = None

    @classmethod
    def initialize(cls, min_size: int = 1, max_size: int = 10) -> None:
        """
        Initialize connection pool.

        Args:
            min_size: Minimum number of connections to maintain
            max_size: Maximum number of connections in the pool
        """
        if not PSYCOPG3_AVAILABLE:
            raise ImportError("psycopg3 is required. Install with: pip install 'psycopg[binary]'")
        if not POOL_AVAILABLE:
            raise ImportError("psycopg_pool is required. Install with: pip install 'psycopg_pool'")

        if cls._pool is None:
            try:
                conninfo = (
                    f"host={settings.POSTGRES_HOST} port={settings.POSTGRES_PORT} "
                    f"user={settings.POSTGRES_USER} password={settings.POSTGRES_PASSWORD} "
                    f"dbname={settings.POSTGRES_DB}"
                )

                cls._pool = ConnectionPool(
                    conninfo,
                    min_size=min_size,
                    max_size=max_size,
                    open=True,  # Open connections immediately
                )
                logger.info(
                    f"PostgreSQL connection pool initialized (psycopg3) - "
                    f"min: {min_size}, max: {max_size}"
                )
            except Exception as e:
                logger.error(f"Failed to initialize PostgreSQL connection pool: {e}")
                raise

    @classmethod
    def get_connection(cls):
        """Get a connection from the pool"""
        if cls._pool is None:
            cls.initialize()
        return cls._pool.getconn()

    @classmethod
    def return_connection(cls, conn):
        """Return a connection to the pool"""
        if cls._pool and conn:
            cls._pool.putconn(conn)

    @classmethod
    def close_all(cls):
        """Close all connections in the pool"""
        if cls._pool:
            cls._pool.close()
            cls._pool = None
            logger.info("PostgreSQL connection pool closed")


@contextmanager
def get_db_connection() -> Generator:
    """Context manager for database connections"""
    conn = None
    try:
        conn = PostgreSQLConnectionPool.get_connection()
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            PostgreSQLConnectionPool.return_connection(conn)
