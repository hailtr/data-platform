"""
Test Redpanda connection script
"""

import sys

# import json
from pathlib import Path
from kafka import KafkaConsumer, KafkaAdminClient

# from kafka.errors import KafkaError

# Add foundation to path
project_root = Path(__file__).parent.parent
foundation_path = project_root / "foundation"
sys.path.insert(0, str(foundation_path))
sys.path.insert(0, str(project_root))

from shared.config.settings import settings  # noqa: E402


def test_connection():
    print(f"Testing connection to Redpanda at {settings.KAFKA_BOOTSTRAP_SERVERS}...")

    try:
        # Test Admin Client
        print("Attempting to connect via KafkaAdminClient...")
        admin = KafkaAdminClient(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
        print("Connected! Listing topics...")
        topics = admin.list_topics()
        print(f"Topics found: {topics}")
        admin.close()

        # Test Consumer
        print("\nAttempting to create KafkaConsumer...")
        consumer = KafkaConsumer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            request_timeout_ms=5000,
            api_version_auto_timeout_ms=5000,
        )
        print("Consumer created successfully!")
        print(f"Bootstrap connected: {consumer.bootstrap_connected()}")
        consumer.close()

        return True
    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
