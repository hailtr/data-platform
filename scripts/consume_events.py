"""
Example script to consume events from Redpanda topics
"""

import sys
import json
from pathlib import Path

# Add foundation to path
project_root = Path(__file__).parent.parent
foundation_path = project_root / "foundation"
sys.path.insert(0, str(foundation_path))
sys.path.insert(0, str(project_root))

from loguru import logger  # noqa: E402
from shared.messaging import RedpandaConsumer  # noqa: E402
from shared.config import settings  # noqa: E402


def main():
    """Consume events from all topics"""
    print("=" * 60)
    print("EVENT CONSUMER - Real-time Event Monitoring")
    print("=" * 60)
    print("\nConsuming from topics:")
    print(f"  - {settings.KAFKA_TOPIC_ORDERS}")
    print(f"  - {settings.KAFKA_TOPIC_PAGE_VIEWS}")
    print(f"  - {settings.KAFKA_TOPIC_INVENTORY}")
    print("\nPress Ctrl+C to stop\n")

    topics = [
        settings.KAFKA_TOPIC_ORDERS,
        settings.KAFKA_TOPIC_PAGE_VIEWS,
        settings.KAFKA_TOPIC_INVENTORY,
    ]

    try:
        consumer = RedpandaConsumer(
            topics=topics,
            group_id="event_monitor",
            auto_offset_reset="latest",  # Start from latest messages
        )

        def message_handler(value, key, partition, offset):
            # Determine event type from topic (we'll need to track this)
            # For now, just show the data
            print(f"\n[Event] Partition={partition}, Offset={offset}")
            if key:
                print(f"  Key: {key}")
            print(f"  Data: {json.dumps(value, indent=2)}")

        # Consume indefinitely
        consumer.consume(handler=message_handler, max_messages=None, timeout_ms=1000)  # Unlimited

    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
