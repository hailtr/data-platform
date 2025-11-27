"""
Redpanda/Kafka producer implementation
"""
import json
from typing import Dict, Any, Optional, Callable, TYPE_CHECKING
from kafka import KafkaProducer
from kafka.errors import KafkaError
from loguru import logger

if TYPE_CHECKING:
    from shared.config.settings import Settings

# Default settings import (fallback)
try:
    from shared.config.settings import settings as default_settings
except ImportError:
    default_settings = None


class RedpandaProducer:
    """Producer for publishing events to Redpanda/Kafka"""
    
    def __init__(
        self, 
        bootstrap_servers: Optional[str] = None,
        settings: Optional['Settings'] = None
    ):
        """
        Initialize Redpanda producer
        
        Args:
            bootstrap_servers: Kafka bootstrap servers (overrides settings)
            settings: Settings instance (defaults to shared.config.settings)
        """
        # Use provided settings or fallback to default
        self.settings = settings or default_settings
        
        if not self.settings:
            raise ValueError("Settings must be provided or available from shared.config.settings")
        
        self.bootstrap_servers = bootstrap_servers or self.settings.KAFKA_BOOTSTRAP_SERVERS
        
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Wait for all replicas
                retries=3,
                max_in_flight_requests_per_connection=1,
                enable_idempotence=True,
                request_timeout_ms=5000
                # Let Kafka auto-detect API version (Redpanda supports modern Kafka APIs)
            )
            logger.info(f"Redpanda producer initialized: {self.bootstrap_servers}")
        except Exception as e:
            error_msg = str(e).lower()
            logger.error(f"Failed to initialize Redpanda producer: {e}")
            
            # Provide helpful error messages
            if 'could not connect' in error_msg or 'timeout' in error_msg or 'connection refused' in error_msg:
                logger.error(
                    f"Cannot connect to Redpanda at {self.bootstrap_servers}. "
                    "Possible causes:\n"
                    "  - Docker services not running (run: docker-compose up -d)\n"
                    "  - Redpanda container not started\n"
                    "  - Wrong host/port configuration\n"
                    "  - Firewall blocking connection"
                )
            raise
    
    def publish(
        self,
        topic: str,
        event: Dict[str, Any],
        key: Optional[str] = None
    ) -> bool:
        """
        Publish event to topic
        
        Args:
            topic: Topic name
            event: Event data (dict)
            key: Optional partition key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            future = self.producer.send(
                topic=topic,
                value=event,
                key=key
            )
            
            # Wait for the message to be sent
            record_metadata = future.get(timeout=10)
            
            logger.debug(
                f"Published to topic={record_metadata.topic}, "
                f"partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}"
            )
            
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to publish to topic {topic}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error publishing to {topic}: {e}")
            return False
    
    def publish_batch(
        self,
        topic: str,
        events: list[Dict[str, Any]],
        key_extractor: Optional[Callable[[Dict[str, Any]], Optional[str]]] = None
    ) -> int:
        """
        Publish multiple events to topic
        
        Args:
            topic: Topic name
            events: List of event data (dicts)
            key_extractor: Optional function to extract key from event
            
        Returns:
            Number of successfully published events
        """
        success_count = 0
        
        for event in events:
            key = None
            if key_extractor:
                key = key_extractor(event)
            
            if self.publish(topic, event, key):
                success_count += 1
        
        logger.info(f"Published {success_count}/{len(events)} events to {topic}")
        return success_count
    
    def close(self):
        """Close producer and flush pending messages"""
        try:
            self.producer.flush(timeout=10)
            self.producer.close()
            logger.info("Redpanda producer closed")
        except Exception as e:
            logger.error(f"Error closing producer: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

