"""
Quick verification script to check if all components are working
"""

import sys
from pathlib import Path

# Add foundation and project to path
project_root = Path(__file__).parent.parent
foundation_path = project_root / "foundation"
project_path = project_root / "projects" / "ecommerce-dbt"
sys.path.insert(0, str(foundation_path))
sys.path.insert(0, str(project_path))
sys.path.insert(0, str(project_root))

from loguru import logger  # noqa: F401, E402


def check_imports():
    """Verify all imports work"""
    print("=" * 60)
    print("VERIFYING IMPORTS")
    print("=" * 60)

    try:
        from shared.models import Order, PageView, Inventory  # noqa: F401

        print("[OK] Data models imported")
    except Exception as e:
        print(f"[ERROR] Data models import failed: {e}")
        return False

    try:
        from shared.config import settings  # noqa: F401

        print("[OK] Configuration imported")
    except Exception as e:
        print(f"[ERROR] Configuration import failed: {e}")
        return False

    try:
        from shared.messaging import RedpandaProducer, RedpandaConsumer  # noqa: F401

        print("[OK] Messaging clients imported")
    except Exception as e:
        print(f"[ERROR] Messaging import failed: {e}")
        return False

    try:
        from shared.database import PostgreSQLConnectionPool, get_db_connection  # noqa: F401

        print("[OK] Database utilities imported")
    except Exception as e:
        print(f"[ERROR] Database import failed: {e}")
        return False

    try:
        from ingestion.kafka_consumer import OrdersIngestionPipeline  # noqa: F401

        print("[OK] Ingestion pipeline imported")
    except Exception as e:
        print(f"[ERROR] Ingestion import failed: {e}")
        return False

    try:
        from data_generator.main import DataGenerator  # noqa: F401

        print("[OK] Data generator imported")
    except Exception as e:
        print(f"[ERROR] Data generator import failed: {e}")
        return False

    return True


def check_configuration():
    """Verify configuration is set up"""
    print("\n" + "=" * 60)
    print("VERIFYING CONFIGURATION")
    print("=" * 60)

    try:
        from shared.config import settings

        print(f"  PostgreSQL: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
        print(f"  Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        print(f"  Kafka: {settings.KAFKA_BOOTSTRAP_SERVERS}")

        # Check for optional project-specific settings
        if hasattr(settings, "DUCKDB_PATH"):
            print(f"  DuckDB: {settings.DUCKDB_PATH}")
        else:
            print("  DuckDB: (not configured in base settings)")

        if hasattr(settings, "KAFKA_TOPIC_ORDERS"):
            print(
                f"  Topics: {settings.KAFKA_TOPIC_ORDERS}, {settings.KAFKA_TOPIC_PAGE_VIEWS}, "
                f"{settings.KAFKA_TOPIC_INVENTORY}"
            )
        else:
            print("  Topics: (project-specific, not in base settings)")

        print("[OK] Configuration loaded")
        return True
    except Exception as e:
        print(f"[ERROR] Configuration check failed: {e}")
        return False


def main():
    """Run all verification checks"""
    print("\n" + "=" * 60)
    print("DATA PLATFORM SETUP VERIFICATION")
    print("=" * 60)
    print("\nThis script verifies that:")
    print("  1. All imports work correctly")
    print("  2. Configuration is properly set up")
    print("\nFor full verification, also run:")
    print("  - python scripts/check_services.py  (check if Docker services are running)")
    print("  - python scripts/test_db_connection.py")
    print("  - python scripts/test_redpanda.py")
    print()

    all_ok = True

    # Check imports
    if not check_imports():
        all_ok = False

    # Check configuration
    if not check_configuration():
        all_ok = False

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    if all_ok:
        print("\n[SUCCESS] All basic checks passed!")
        print("\nNext steps:")
        print("  1. Start services: docker-compose up -d")
        print("  2. Test database: python scripts/test_db_connection.py")
        print("  3. Test Redpanda: python scripts/test_redpanda.py")
        print("  4. Generate data: python projects/ecommerce-dbt/data_generator/main.py 10")
        sys.exit(0)
    else:
        print("\n[FAILED] Some checks failed. Please review errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
