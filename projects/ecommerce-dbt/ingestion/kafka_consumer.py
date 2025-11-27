"""
Kafka consumer pipeline for ingesting events into data warehouse
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

# Add foundation to path
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
foundation_path = project_root / "foundation"
sys.path.insert(0, str(foundation_path))
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.messaging import RedpandaConsumer
from shared.database import PostgreSQLConnectionPool, get_db_connection
from config import settings  # Project-specific config


class OrdersIngestionPipeline:
    """Pipeline to ingest orders from Kafka to data warehouse"""
    
    def __init__(self, consumer_group: str = "orders_ingestion", batch_size: int = 100):
        self.consumer_group = consumer_group
        self.consumer = None
        self.batch_size = batch_size
        self.batch: List[Dict[str, Any]] = []
    
    def _insert_batch(self):
        """Insert batch of orders into PostgreSQL"""
        if not self.batch:
            return
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    insert_query = """
                        INSERT INTO orders (order_id, user_id, product_id, timestamp, amount, status, quantity)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (order_id) DO UPDATE SET
                            amount = EXCLUDED.amount,
                            status = EXCLUDED.status,
                            quantity = EXCLUDED.quantity,
                            updated_at = CURRENT_TIMESTAMP
                    """
                    
                    values = [
                        (
                            order['order_id'],
                            order['user_id'],
                            order['product_id'],
                            datetime.fromisoformat(order['timestamp'].replace('Z', '+00:00')),
                            float(order['amount']),
                            order['status'],
                            int(order.get('quantity', 1))
                        )
                        for order in self.batch
                    ]
                    
                    cur.executemany(insert_query, values)
                    logger.info(f"Inserted {len(self.batch)} orders into PostgreSQL")
                    self.batch.clear()
        except Exception as e:
            logger.error(f"Error inserting orders batch: {e}")
            self.batch.clear()  # Clear batch on error to avoid retrying forever
            raise
    
    def start(self):
        """Start consuming and ingesting orders"""
        logger.info("Starting orders ingestion pipeline...")
        
        # Initialize database connection pool
        PostgreSQLConnectionPool.initialize()
        
        self.consumer = RedpandaConsumer(
            topics=[settings.KAFKA_TOPIC_ORDERS],
            group_id=self.consumer_group,
            auto_offset_reset='earliest',
            settings=settings
        )
        
        def process_order(value: Dict[str, Any], key: Optional[str], partition: int, offset: int):
            """Process a single order event"""
            try:
                logger.debug(f"Processing order: {value.get('order_id')}")
                self.batch.append(value)
                
                if len(self.batch) >= self.batch_size:
                    self._insert_batch()
            except Exception as e:
                logger.error(f"Error processing order {value.get('order_id')}: {e}")
        
        try:
            self.consumer.consume(handler=process_order, max_messages=None)
        finally:
            # Insert any remaining items in batch
            if self.batch:
                self._insert_batch()
    
    def stop(self):
        """Stop the pipeline"""
        if self.batch:
            self._insert_batch()
        if self.consumer:
            self.consumer.close()
        logger.info("Orders ingestion pipeline stopped")


class PageViewsIngestionPipeline:
    """Pipeline to ingest page views from Kafka to data warehouse"""
    
    def __init__(self, consumer_group: str = "page_views_ingestion", batch_size: int = 100):
        self.consumer_group = consumer_group
        self.consumer = None
        self.batch_size = batch_size
        self.batch: List[Dict[str, Any]] = []
    
    def _insert_batch(self):
        """Insert batch of page views into PostgreSQL"""
        if not self.batch:
            return
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    insert_query = """
                        INSERT INTO page_views (view_id, user_id, product_id, timestamp, session_id, page_url, duration_seconds)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (view_id) DO NOTHING
                    """
                    
                    values = [
                        (
                            view['view_id'],
                            view['user_id'],
                            view.get('product_id'),
                            datetime.fromisoformat(view['timestamp'].replace('Z', '+00:00')),
                            view['session_id'],
                            view['page_url'],
                            float(view['duration_seconds']) if view.get('duration_seconds') else None
                        )
                        for view in self.batch
                    ]
                    
                    cur.executemany(insert_query, values)
                    logger.info(f"Inserted {len(self.batch)} page views into PostgreSQL")
                    self.batch.clear()
        except Exception as e:
            logger.error(f"Error inserting page views batch: {e}")
            self.batch.clear()
            raise
    
    def start(self):
        """Start consuming and ingesting page views"""
        logger.info("Starting page views ingestion pipeline...")
        
        # Initialize database connection pool
        PostgreSQLConnectionPool.initialize()
        
        self.consumer = RedpandaConsumer(
            topics=[settings.KAFKA_TOPIC_PAGE_VIEWS],
            group_id=self.consumer_group,
            auto_offset_reset='earliest',
            settings=settings
        )
        
        def process_page_view(value: Dict[str, Any], key: Optional[str], partition: int, offset: int):
            """Process a single page view event"""
            try:
                logger.debug(f"Processing page view: {value.get('view_id')}")
                self.batch.append(value)
                
                if len(self.batch) >= self.batch_size:
                    self._insert_batch()
            except Exception as e:
                logger.error(f"Error processing page view {value.get('view_id')}: {e}")
        
        try:
            self.consumer.consume(handler=process_page_view, max_messages=None)
        finally:
            # Insert any remaining items in batch
            if self.batch:
                self._insert_batch()
    
    def stop(self):
        """Stop the pipeline"""
        if self.batch:
            self._insert_batch()
        if self.consumer:
            self.consumer.close()
        logger.info("Page views ingestion pipeline stopped")


class InventoryIngestionPipeline:
    """Pipeline to ingest inventory changes from Kafka to data warehouse"""
    
    def __init__(self, consumer_group: str = "inventory_ingestion", batch_size: int = 100):
        self.consumer_group = consumer_group
        self.consumer = None
        self.batch_size = batch_size
        self.batch: List[Dict[str, Any]] = []
    
    def _insert_batch(self):
        """Insert batch of inventory changes into PostgreSQL"""
        if not self.batch:
            return
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    insert_query = """
                        INSERT INTO inventory_changes (product_id, timestamp, stock_change, current_stock, warehouse_id)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    
                    values = [
                        (
                            inv['product_id'],
                            datetime.fromisoformat(inv['timestamp'].replace('Z', '+00:00')),
                            int(inv['stock_change']),
                            int(inv['current_stock']),
                            inv.get('warehouse_id')
                        )
                        for inv in self.batch
                    ]
                    
                    cur.executemany(insert_query, values)
                    logger.info(f"Inserted {len(self.batch)} inventory changes into PostgreSQL")
                    self.batch.clear()
        except Exception as e:
            logger.error(f"Error inserting inventory batch: {e}")
            self.batch.clear()
            raise
    
    def start(self):
        """Start consuming and ingesting inventory changes"""
        logger.info("Starting inventory ingestion pipeline...")
        
        # Initialize database connection pool
        PostgreSQLConnectionPool.initialize()
        
        self.consumer = RedpandaConsumer(
            topics=[settings.KAFKA_TOPIC_INVENTORY],
            group_id=self.consumer_group,
            auto_offset_reset='earliest',
            settings=settings
        )
        
        def process_inventory(value: Dict[str, Any], key: Optional[str], partition: int, offset: int):
            """Process a single inventory change event"""
            try:
                logger.debug(f"Processing inventory: {value.get('product_id')}")
                self.batch.append(value)
                
                if len(self.batch) >= self.batch_size:
                    self._insert_batch()
            except Exception as e:
                logger.error(f"Error processing inventory {value.get('product_id')}: {e}")
        
        try:
            self.consumer.consume(handler=process_inventory, max_messages=None)
        finally:
            # Insert any remaining items in batch
            if self.batch:
                self._insert_batch()
    
    def stop(self):
        """Stop the pipeline"""
        if self.batch:
            self._insert_batch()
        if self.consumer:
            self.consumer.close()
        logger.info("Inventory ingestion pipeline stopped")

