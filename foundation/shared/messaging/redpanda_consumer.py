"""
Redpanda/Kafka consumer implementation
"""
import json
from typing import Callable, Optional, Dict, Any, TYPE_CHECKING
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from loguru import logger

if TYPE_CHECKING:
    from shared.config.settings import Settings

# Default settings import (fallback)
try:
    from shared.config.settings import settings as default_settings
except ImportError:
    default_settings = None


class RedpandaConsumer:
    """Consumer for reading events from Redpanda/Kafka"""
    
    def __init__(
        self,
        topics: list[str],
        group_id: str,
        bootstrap_servers: Optional[str] = None,
        auto_offset_reset: str = 'earliest',
        settings: Optional['Settings'] = None
    ):
        """
        Initialize Redpanda consumer
        
        Args:
            topics: List of topic names to consume
            group_id: Consumer group ID
            bootstrap_servers: Kafka bootstrap servers (overrides settings)
            auto_offset_reset: Where to start reading ('earliest' or 'latest')
            settings: Settings instance (defaults to shared.config.settings)
        """
        # Use provided settings or fallback to default
        self.settings = settings or default_settings
        
        if not self.settings:
            raise ValueError("Settings must be provided or available from shared.config.settings")
        
        self.bootstrap_servers = bootstrap_servers or self.settings.KAFKA_BOOTSTRAP_SERVERS
        self.topics = topics
        self.group_id = group_id
        
        try:
            self.consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                auto_offset_reset=auto_offset_reset,
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                consumer_timeout_ms=1000  # Timeout for polling
                # Let Kafka auto-detect API version (Redpanda supports modern Kafka APIs)
                # Request timeout will use default (must be > session timeout)
            )
            logger.info(
                f"Redpanda consumer initialized: "
                f"topics={topics}, group_id={group_id}, "
                f"servers={self.bootstrap_servers}"
            )
        except Exception as e:
            error_msg = str(e).lower()
            logger.error(f"Failed to initialize Redpanda consumer: {e}")
            
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
    
    def consume(
        self,
        handler: Callable[[Dict[str, Any], Optional[str], int, int], None],
        max_messages: Optional[int] = None,
        timeout_ms: int = 1000
    ):
        """
        Consume messages and call handler for each
        
        Args:
            handler: Function(value, key, partition, offset) -> None
            max_messages: Maximum number of messages to consume (None = unlimited)
            timeout_ms: Polling timeout in milliseconds
        """
        message_count = 0
        
        try:
            while True:
                if max_messages and message_count >= max_messages:
                    break
                
                message_pack = self.consumer.poll(timeout_ms=timeout_ms)
                
                if not message_pack:
                    continue
                
                for topic_partition, messages in message_pack.items():
                    for message in messages:
                        try:
                            handler(
                                value=message.value,
                                key=message.key,
                                partition=message.partition,
                                offset=message.offset
                            )
                            message_count += 1
                            
                            if max_messages and message_count >= max_messages:
                                break
                                
                        except Exception as e:
                            logger.error(
                                f"Error processing message from "
                                f"{topic_partition.topic}[{topic_partition.partition}]:{message.offset}: {e}"
                            )
                
                if max_messages and message_count >= max_messages:
                    break
                    
        except KeyboardInterrupt:
            logger.info("Consumer stopped by user")
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
            raise
        finally:
            self.close()
    
    def close(self):
        """Close consumer"""
        try:
            self.consumer.close()
            logger.info("Redpanda consumer closed")
        except Exception as e:
            logger.error(f"Error closing consumer: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

