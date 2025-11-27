"""
Test Redpanda connection and basic producer/consumer functionality
"""
import sys
import time
import json
from pathlib import Path

# Add foundation to path
project_root = Path(__file__).parent.parent
foundation_path = project_root / "foundation"
sys.path.insert(0, str(foundation_path))
sys.path.insert(0, str(project_root))

from loguru import logger
from shared.messaging import RedpandaProducer, RedpandaConsumer
from shared.config import settings


def test_producer():
    """Test Redpanda producer"""
    print("=== Testing Redpanda Producer ===\n")
    
    try:
        producer = RedpandaProducer()
        print("[OK] Producer initialized")
        
        # Test publishing a single message
        test_event = {
            "test_id": "test_001",
            "message": "Hello Redpanda!",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        print(f"\nPublishing test message to topic '{settings.KAFKA_TOPIC_ORDERS}'...")
        success = producer.publish(
            topic=settings.KAFKA_TOPIC_ORDERS,
            event=test_event,
            key="test_001"
        )
        
        if success:
            print("[OK] Message published successfully")
        else:
            print("[ERROR] Failed to publish message")
            return False
        
        # Test batch publishing
        print(f"\nPublishing batch of 5 messages...")
        batch_events = [
            {"test_id": f"test_{i:03d}", "message": f"Test message {i}"}
            for i in range(1, 6)
        ]
        
        count = producer.publish_batch(
            topic=settings.KAFKA_TOPIC_ORDERS,
            events=batch_events,
            key_extractor=lambda e: e.get('test_id')
        )
        
        print(f"[OK] Published {count}/{len(batch_events)} messages")
        
        producer.close()
        return True
        
    except Exception as e:
        error_msg = str(e).lower()
        print(f"[ERROR] Producer test failed: {e}")
        
        if 'could not connect' in error_msg or 'timeout' in error_msg or 'connection refused' in error_msg:
            print("\n  This usually means Docker services are not running.")
            print("  Run: python scripts/check_services.py")
            print("  Or start services: docker-compose up -d")
        
        import traceback
        traceback.print_exc()
        return False


def test_consumer():
    """Test Redpanda consumer"""
    print("\n=== Testing Redpanda Consumer ===\n")
    
    try:
        consumer = RedpandaConsumer(
            topics=[settings.KAFKA_TOPIC_ORDERS],
            group_id="test_consumer_group",
            auto_offset_reset='earliest'
        )
        print("[OK] Consumer initialized")
        
        print(f"\nConsuming messages from topic '{settings.KAFKA_TOPIC_ORDERS}'...")
        print("(Will consume up to 10 messages or timeout after 5 seconds)\n")
        
        messages_received = []
        
        def message_handler(value, key, partition, offset):
            messages_received.append({
                'key': key,
                'value': value,
                'partition': partition,
                'offset': offset
            })
            print(f"  [Received] Partition={partition}, Offset={offset}, Key={key}")
            print(f"    Value: {json.dumps(value, indent=2)}")
        
        # Consume messages
        start_time = time.time()
        consumer.consume(
            handler=message_handler,
            max_messages=10,
            timeout_ms=5000
        )
        
        elapsed = time.time() - start_time
        print(f"\n[OK] Consumer test completed")
        print(f"  Messages received: {len(messages_received)}")
        print(f"  Time elapsed: {elapsed:.2f}s")
        
        consumer.close()
        return True
        
    except Exception as e:
        error_msg = str(e).lower()
        print(f"[ERROR] Consumer test failed: {e}")
        
        if 'could not connect' in error_msg or 'timeout' in error_msg or 'connection refused' in error_msg:
            print("\n  This usually means Docker services are not running.")
            print("  Run: python scripts/check_services.py")
            print("  Or start services: docker-compose up -d")
        
        import traceback
        traceback.print_exc()
        return False


def check_services_first():
    """Quick check if services are available"""
    try:
        from scripts.check_services import check_docker_running, check_redpanda
        if not check_docker_running():
            print("[WARNING] Docker is not running. Redpanda tests will fail.")
            print("  Start Docker Desktop and run: docker-compose up -d")
            return False
        if not check_redpanda():
            print("[WARNING] Redpanda is not accessible. Tests will fail.")
            print("  Run: docker-compose up -d redpanda")
            return False
        return True
    except Exception:
        # If check_services fails, continue anyway
        return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("REDPANDA INTEGRATION TEST")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Bootstrap servers: {settings.KAFKA_BOOTSTRAP_SERVERS}")
    print(f"  Topics: {settings.KAFKA_TOPIC_ORDERS}, {settings.KAFKA_TOPIC_PAGE_VIEWS}, {settings.KAFKA_TOPIC_INVENTORY}")
    print()
    
    # Quick service check
    if not check_services_first():
        print("\n[INFO] Continuing with tests anyway...")
        print()
    
    # Test producer
    producer_ok = test_producer()
    
    if not producer_ok:
        print("\n[ERROR] Producer test failed. Skipping consumer test.")
        sys.exit(1)
    
    # Wait a bit for messages to be available
    print("\nWaiting 2 seconds for messages to be available...")
    time.sleep(2)
    
    # Test consumer
    consumer_ok = test_consumer()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"  Producer: {'[OK]' if producer_ok else '[FAILED]'}")
    print(f"  Consumer: {'[OK]' if consumer_ok else '[FAILED]'}")
    
    if producer_ok and consumer_ok:
        print("\n[SUCCESS] All tests passed!")
        sys.exit(0)
    else:
        print("\n[FAILED] Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

