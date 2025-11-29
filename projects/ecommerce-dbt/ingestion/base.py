"""
Base class for ingestion pipelines
Encapsulates common logic for:
- Kafka consumption
- Batching
- Error handling (DLQ)
- Retries
- Graceful shutdown
"""
from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod
from datetime import datetime
from loguru import logger
import time
from functools import wraps

from shared.messaging import RedpandaConsumer, RedpandaProducer
from shared.database import PostgreSQLConnectionPool
from config import settings

def retry_with_backoff(retries=3, backoff_in_seconds=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        raise
                    sleep = (backoff_in_seconds * 2 ** x)
                    logger.warning(f"Attempt {x+1}/{retries} failed with error: {e}. Retrying in {sleep} seconds...")
                    time.sleep(sleep)
                    x += 1
        return wrapper
    return decorator

class BaseIngestionPipeline(ABC):
    """Base class for all ingestion pipelines"""
    
    def __init__(
        self, 
        topic: str,
        consumer_group: str,
        batch_size: int = 100
    ):
        self.topic = topic
        self.consumer_group = consumer_group
        self.batch_size = batch_size
        self.batch: List[Dict[str, Any]] = []
        self.consumer: Optional[RedpandaConsumer] = None
        self.dlq_producer: Optional[RedpandaProducer] = None
        
    @abstractmethod
    def _insert_batch(self):
        """
        Insert the current batch into the database.
        Must be implemented by subclasses.
        Should raise exception on failure to trigger retry/DLQ logic if needed,
        though usually batch insertion failure should crash the pipeline or retry, 
        not DLQ individual messages unless we can identify which one failed.
        """
        pass
        
    def _send_to_dlq(self, event: Dict[str, Any], error: Exception):
        """Send a failed event to the Dead Letter Queue"""
        try:
            if not self.dlq_producer:
                self.dlq_producer = RedpandaProducer(settings=settings)
            
            self.dlq_producer.publish(
                topic=settings.KAFKA_TOPIC_DLQ,
                event={
                    "original_topic": self.topic,
                    "error": str(error),
                    "payload": event,
                    "timestamp": datetime.now().isoformat()
                }
            )
            logger.info(f"Sent failed event to DLQ: {self.topic}")
        except Exception as dlq_error:
            logger.error(f"Failed to send to DLQ: {dlq_error}")

    def start(self):
        """Start the ingestion pipeline"""
        logger.info(f"Starting {self.__class__.__name__} on topic {self.topic}...")
        
        # Initialize database connection pool
        PostgreSQLConnectionPool.initialize()
        
        self.consumer = RedpandaConsumer(
            topics=[self.topic],
            group_id=self.consumer_group,
            auto_offset_reset='earliest',
            settings=settings
        )
        
        def process_message(value: Dict[str, Any], key: Optional[str], partition: int, offset: int):
            """Process a single message"""
            try:
                logger.debug(f"Processing message from {self.topic}")
                self.batch.append(value)
                
                if len(self.batch) >= self.batch_size:
                    self._insert_batch_with_retry()
            except Exception as e:
                logger.error(f"Error processing message from {self.topic}: {e}")
                self._send_to_dlq(value, e)
        
        try:
            self.consumer.consume(handler=process_message, max_messages=None)
        finally:
            # Insert any remaining items in batch
            if self.batch:
                try:
                    self._insert_batch_with_retry()
                except Exception as e:
                    logger.error(f"Failed to insert final batch: {e}")
                    # In a real scenario, we might want to DLQ the whole batch or dump to disk
                    
    @retry_with_backoff(retries=3, backoff_in_seconds=1)
    def _insert_batch_with_retry(self):
        """Wrapper for _insert_batch with retry logic"""
        try:
            self._insert_batch()
        except Exception as e:
            # If retries are exhausted, re-raise to let the caller handle it
            logger.error(f"Failed to insert batch after retries: {e}")
            raise

    def stop(self):
        """Stop the pipeline"""
        if self.batch:
            try:
                self._insert_batch_with_retry()
            except Exception as e:
                logger.error(f"Error flushing batch on stop: {e}")
                
        if self.consumer:
            self.consumer.close()
        if self.dlq_producer:
            self.dlq_producer.close()
            
        logger.info(f"{self.__class__.__name__} stopped")
