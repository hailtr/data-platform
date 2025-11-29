"""
Initialize PostgreSQL database schema
"""

# import os
from pathlib import Path
from loguru import logger
from shared.database.postgres_connection import get_db_connection


def run_migrations():
    """Run database migrations"""
    migrations_dir = Path(__file__).parent / "migrations"

    # Get all SQL files sorted by name
    sql_files = sorted(migrations_dir.glob("*.sql"))

    if not sql_files:
        logger.warning("No migration files found")
        return

    logger.info(f"Running {len(sql_files)} migration(s)...")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for sql_file in sql_files:
                logger.info(f"Running migration: {sql_file.name}")
                with open(sql_file, "r", encoding="utf-8", errors="ignore") as f:
                    sql_content = f.read()
                    # Execute each statement separately
                    statements = [s.strip() for s in sql_content.split(";") if s.strip()]
                    for statement in statements:
                        if statement:
                            cur.execute(statement)
                logger.info(f"Migration {sql_file.name} completed")

    logger.info("All migrations completed successfully")


if __name__ == "__main__":
    from shared.database.postgres_connection import PostgreSQLConnectionPool

    PostgreSQLConnectionPool.initialize()
    run_migrations()
