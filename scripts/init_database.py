"""
Initialize database schema
Run this script to create all necessary tables in PostgreSQL
"""

import sys
from pathlib import Path

# Add foundation to path
project_root = Path(__file__).parent.parent
foundation_path = project_root / "foundation"
sys.path.insert(0, str(foundation_path))
sys.path.insert(0, str(project_root))

from loguru import logger  # noqa: E402
from shared.database import PostgreSQLConnectionPool, run_migrations  # noqa: E402
from shared.config.settings import settings  # noqa: E402


def create_database_if_not_exists(db_name: str):
    """Create database if it doesn't exist"""
    import psycopg

    # Connect to default postgres database to create the target database
    conninfo = (
        f"host={settings.POSTGRES_HOST} port={settings.POSTGRES_PORT} "
        f"user={settings.POSTGRES_USER} password={settings.POSTGRES_PASSWORD} "
        f"dbname=postgres"
    )

    try:
        with psycopg.connect(conninfo, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Check if database exists
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
                exists = cur.fetchone()

                if not exists:
                    logger.info(f"Creating database '{db_name}'...")
                    cur.execute(f'CREATE DATABASE "{db_name}"')
                    logger.info(f"Database '{db_name}' created successfully")
                else:
                    logger.info(f"Database '{db_name}' already exists")
    except Exception as e:
        logger.error(f"Error creating database '{db_name}': {e}")
        raise


if __name__ == "__main__":
    logger.info("Initializing PostgreSQL database...")
    try:
        # Create database if it doesn't exist (for project-specific databases)
        db_name = getattr(settings, "POSTGRES_DB", "postgres")
        if db_name != "postgres":
            create_database_if_not_exists(db_name)

        # Initialize connection pool and run migrations
        PostgreSQLConnectionPool.initialize()
        run_migrations()
        logger.info("Database initialization completed successfully!")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        PostgreSQLConnectionPool.close_all()
