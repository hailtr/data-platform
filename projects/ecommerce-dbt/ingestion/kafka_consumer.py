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

from shared.database import get_db_connection
from config import settings
from ingestion.base import BaseIngestionPipeline, retry_with_backoff


class OrdersIngestionPipeline(BaseIngestionPipeline):
    """Pipeline to ingest orders from Kafka to data warehouse"""
    
    def __init__(self, consumer_group: str = "orders_ingestion", batch_size: int = 100):
        super().__init__(
            topic=settings.KAFKA_TOPIC_ORDERS,
            consumer_group=consumer_group,
            batch_size=batch_size
        )
    
    @retry_with_backoff(retries=3, backoff_in_seconds=1)
    def _insert_batch(self):
        """Insert batch of orders into PostgreSQL"""
        if not self.batch:
            return
        
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


class PageViewsIngestionPipeline(BaseIngestionPipeline):
    """Pipeline to ingest page views from Kafka to data warehouse"""
    
    def __init__(self, consumer_group: str = "page_views_ingestion", batch_size: int = 100):
        super().__init__(
            topic=settings.KAFKA_TOPIC_PAGE_VIEWS,
            consumer_group=consumer_group,
            batch_size=batch_size
        )
    
    @retry_with_backoff(retries=3, backoff_in_seconds=1)
    def _insert_batch(self):
        """Insert batch of page views into PostgreSQL"""
        if not self.batch:
            return
        
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


class InventoryIngestionPipeline(BaseIngestionPipeline):
    """Pipeline to ingest inventory changes from Kafka to data warehouse"""
    
    def __init__(self, consumer_group: str = "inventory_ingestion", batch_size: int = 100):
        super().__init__(
            topic=settings.KAFKA_TOPIC_INVENTORY,
            consumer_group=consumer_group,
            batch_size=batch_size
        )
    
    @retry_with_backoff(retries=3, backoff_in_seconds=1)
    def _insert_batch(self):
        """Insert batch of inventory changes into PostgreSQL"""
        if not self.batch:
            return
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                insert_query = """
                    INSERT INTO inventory_changes (product_id, timestamp, stock_change, current_stock, warehouse_id)
                    VALUES (%s, %s, %s, %s, %s)
                """
                
                values = [
                    (
                        inv['product_id'],
                        inv.get('timestamp') and datetime.fromisoformat(inv['timestamp'].replace('Z', '+00:00')),
                        int(inv['stock_change']),
                        int(inv['current_stock']),
                        inv.get('warehouse_id')
                    )
                    for inv in self.batch
                ]
                
                cur.executemany(insert_query, values)
                logger.info(f"Inserted {len(self.batch)} inventory changes into PostgreSQL")
                self.batch.clear()
