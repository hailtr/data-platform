import json
import time
import datetime
import random
import os
from kafka import KafkaProducer

BROKERS = os.getenv('REDPANDA_BROKERS', 'localhost:9092')
TOPIC = 'events-stream'

import uuid

# User Database to maintain consistency (User 5 always comes from US)
USER_DB = {}

def get_user_profile(user_id):
    if user_id not in USER_DB:
        USER_DB[user_id] = {
            'country': random.choice(['US', 'CA', 'UK', 'DE', 'FR', 'BR', 'JP']),
            'device_type': random.choice(['mobile', 'desktop', 'tablet']),
            'subscription_tier': random.choice(['free', 'premium', 'enterprise'])
        }
    return USER_DB[user_id]

def generate_session_events(base_timestamp):
    """Generates a sequence of events for a single user session"""
    events = []
    user_id = random.randint(1, 100)
    profile = get_user_profile(user_id)
    
    session_length = random.randint(1, 10)
    session_id = str(uuid.uuid4())
    current_time = base_timestamp
    
    # Session Context
    referrer = random.choice(['google', 'facebook', 'direct', 'email', 'twitter'])
    if random.random() < 0.1: referrer = None # Direct traffic usually null or 'direct'
    
    # Ad Context (Campaigns depend on country)
    ad_id = None
    campaign_id = None
    if referrer in ['google', 'facebook', 'twitter']:
        ad_id = f"ad_{random.randint(1000, 9999)}"
        campaign_id = f"cmp_{profile['country']}_{random.choice(['summer', 'blackfriday', 'welcome'])}"

    for _ in range(session_length):
        current_time += random.uniform(1, 30)
        
        # Action Probability
        rand_val = random.random()
        if rand_val < 0.7: action = 'view'
        elif rand_val < 0.9: action = 'click'
        elif rand_val < 0.98: action = 'purchase'
        else: action = 'error'

        # Value Logic
        value = 0.0
        if action == 'view': value = 0.01
        elif action == 'click': value = 0.50
        elif action == 'purchase': value = round(random.uniform(5.0, 200.0), 2)
        elif action == 'error': value = 0.0

        # Dirty Data (5% - Country mismatch context)
        country = profile['country'] # Default correct
        if random.random() < 0.01:
            country = 'XX' # Invalid country code

        events.append({
            'event_id': str(uuid.uuid4()),
            'timestamp': current_time,
            'session_id': session_id,
            'user_id': user_id,
            'country': country,
            'device_type': profile['device_type'],
            'action': action,
            'value': value,
            'context': {
                'referrer': referrer,
                'ad_id': ad_id,
                'campaign_id': campaign_id,
                'url': f"https://shop.com/{profile['country']}/{random.choice(['home', 'product', 'cart'])}"
            }
        })
        
        if action == 'error' or action == 'purchase':
            break
            
    return events

from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

# Logger configured above

def main():
    logger.info(f"Connecting to Redpanda at {BROKERS}...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=BROKERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Failed to connect to Redpanda: {e}")
        return

    logger.success(f"Connected! Producing SESSION events to topic '{TOPIC}'...")
    
    try:
        while True:
            # Simulate a user starting a session "now"
            now = time.time()
            session_batch = generate_session_events(now)
            session_id = session_batch[0]['session_id'] if session_batch else "N/A"
            user_id = session_batch[0]['user_id'] if session_batch else "N/A"

            logger.info(f"New Session: {session_id} (User {user_id}) - {len(session_batch)} events")
            
            for event in session_batch:
                producer.send(TOPIC, event)
                # logger.debug(f"  -> {event['action']} ({event['value']})") # Optional noisy usage
                print(f"  -> {event['action']:<10} | Value: {str(event['value']):<8} | {datetime.datetime.fromtimestamp(event['timestamp']).strftime('%H:%M:%S')}")
                time.sleep(0.1) # Fast emit of the session
            
            # Pause between different user sessions
            time.sleep(random.uniform(0.5, 2.0))
            
    except KeyboardInterrupt:
        logger.warning("Stopping producer...")
    finally:
        if 'producer' in locals():
            producer.close()
            logger.info("Producer closed")

if __name__ == '__main__':
    main()
