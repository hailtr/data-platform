"""
Test database connection script.
Useful for debugging connection issues and verifying database setup.

Usage:
    python scripts/test_db_connection.py
"""

import sys
import codecs
from pathlib import Path

# Fix encoding for Windows console
try:
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout = codecs.getwriter("utf8")(sys.stdout.buffer, "strict")
except Exception:
    pass

# Add foundation to path
project_root = Path(__file__).parent.parent
foundation_path = project_root / "foundation"
sys.path.insert(0, str(foundation_path))
sys.path.insert(0, str(project_root))

import psycopg  # noqa: E402
from psycopg import OperationalError  # noqa: E402
from shared.config import settings  # noqa: E402


def test_connection():
    """Test PostgreSQL connection"""
    print("=== Testing PostgreSQL Connection ===\n")

    print("Configuration:")
    print(f"  Host: {settings.POSTGRES_HOST}")
    print(f"  Port: {settings.POSTGRES_PORT}")
    print(f"  User: {settings.POSTGRES_USER}")
    print(f"  Database: {settings.POSTGRES_DB}")
    print()

    try:
        print("Attempting connection...")
        conn = psycopg.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            dbname=settings.POSTGRES_DB,
            connect_timeout=5,
        )

        with conn.cursor() as cur:
            cur.execute("SELECT version(), current_database(), current_user;")
            row = cur.fetchone()

        print("\n[OK] Connection successful!")
        print(f"  PostgreSQL version: {row[0][:60]}...")
        print(f"  Current database: {row[1]}")
        print(f"  Current user: {row[2]}")

        conn.close()
        return True

    except OperationalError as e:
        error_msg = str(e)
        print(f"\n[ERROR] Connection failed: {type(e).__name__}")

        if "password authentication failed" in error_msg.lower():
            print("\n  Issue: Password authentication failed")
            print("  Possible causes:")
            print("    - Incorrect password in settings")
            print("    - PostgreSQL user/password mismatch")
            print("    - pg_hba.conf configuration issue")
        elif "could not connect" in error_msg.lower() or "timeout" in error_msg.lower():
            print("\n  Issue: Cannot reach database server")
            print("  Possible causes:")
            print("    - Docker services not running")
            print("      → Start Docker Desktop")
            print("      → Run: docker-compose up -d postgres")
            print("    - Database container not running")
            print("    - Wrong host/port configuration")
            print("    - Port conflict with another service")
            print("    - Firewall blocking connection")
            print(
                "\n  Quick check: Run 'python scripts/check_services.py' to verify Docker services"
            )
        else:
            print(f"  Error details: {error_msg[:200]}")

        return False

    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {type(e).__name__}")
        print(f"  {e}")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
