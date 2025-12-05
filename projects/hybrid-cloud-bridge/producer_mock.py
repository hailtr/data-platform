import json
import time
import random
import os
from kafka import KafkaProducer

BROKERS = os.getenv('REDPANDA_BROKERS', 'localhost:9092')
TOPIC = 'events-stream'

def generate_event():
    return {
        'event_id': random.randint(1000, 9999),
        'timestamp': time.time(),
        'user_id': random.randint(1, 100),
        'action': random.choice(['click', 'view', 'purchase']),
        'value': round(random.uniform(10.0, 500.0), 2)
    }

def main():
    print(f"Connecting to Redpanda at {BROKERS}...")
    producer = KafkaProducer(
        bootstrap_servers=BROKERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    print(f"Producing events to topic '{TOPIC}'...")
    try:
        while True:
            event = generate_event()
            producer.send(TOPIC, event)
            print(f"Sent: {event}")
            time.sleep(0.1)  # 10 events per second
    except KeyboardInterrupt:
        print("Stopping producer...")
    finally:
        producer.close()

if __name__ == '__main__':
    main()
