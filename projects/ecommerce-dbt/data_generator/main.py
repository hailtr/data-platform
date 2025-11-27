"""
Main data generator script
Generates synthetic e-commerce events and publishes them to Redpanda/Kafka
"""
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import asdict
from loguru import logger

# Add paths: project root and foundation
project_root = Path(__file__).parent.parent.parent.parent
foundation_path = project_root / "foundation"
sys.path.insert(0, str(foundation_path))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import project-specific config
from config import settings  # Project-specific config

# Import shared code
from data_generator.config import GeneratorConfig
from data_generator.event_generator import EventGenerator
from shared.messaging import RedpandaProducer


class DataGenerator:
    """Main data generator orchestrator"""
    
    def __init__(self, config: Optional[GeneratorConfig] = None, producer: Optional[RedpandaProducer] = None):
        self.config = config or GeneratorConfig()
        self.event_gen = EventGenerator(self.config)
        self.producer = producer
        self.running = False
    
    def generate_and_publish_stream(
        self,
        duration_seconds: Optional[int] = None,
        events_per_batch: int = 10
    ):
        """
        Generate events in real-time and publish to message queue
        
        Args:
            duration_seconds: How long to generate (None = infinite)
            events_per_batch: How many events to generate per batch
        """
        logger.info("Starting data generation stream...")
        logger.info(f"Config: {events_per_batch} events per batch")
        
        self.running = True
        start_time = datetime.now()
        
        try:
            # Use a batch window to ensure we get orders/inventory
            # (since rates are < 1 per second, we need multiple seconds per batch)
            batch_window_seconds = 10  # Generate 10 seconds worth of events per batch
            last_publish_time = datetime.now()
            
            while self.running:
                batch_start = datetime.now()
                
                # Generate batch of events for the full window
                # This ensures we get orders (0.5/sec * 10 = 5 orders) and inventory (0.1/sec * 10 = 1)
                orders, page_views, inventory = self.event_gen.generate_batch(
                    duration_seconds=batch_window_seconds,
                    start_time=batch_start
                )
                
                # Publish immediately (batch already contains window worth of events)
                if self.producer:
                    self._publish_events(orders, page_views, inventory)
                else:
                    logger.debug(
                        f"Generated: {len(orders)} orders, "
                        f"{len(page_views)} page views, "
                        f"{len(inventory)} inventory changes"
                    )
                
                last_publish_time = datetime.now()
                
                # Check if we should stop
                if duration_seconds:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed >= duration_seconds:
                        break
                
                # Sleep to maintain rate
                time.sleep(1.0)
                
        except KeyboardInterrupt:
            logger.info("Data generation stopped by user")
        finally:
            self.running = False
            logger.info("Data generation stopped")
    
    def generate_historical_batch(
        self,
        days: int = 30,
        output_format: str = "events"  # "events" or "database"
    ):
        """
        Generate historical data batch
        
        Args:
            days: Number of days of historical data
            output_format: "events" (for streaming) or "database" (direct insert)
        """
        logger.info(f"Generating {days} days of historical data...")
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Generate data day by day
        for day in range(days):
            day_start = start_date + timedelta(days=day)
            day_end = day_start + timedelta(days=1)
            
            logger.info(f"Generating data for day {day + 1}/{days}: {day_start.date()}")
            
            # Generate events for this day
            orders, page_views, inventory = self.event_gen.generate_batch(
                duration_seconds=86400,  # Full day
                start_time=day_start
            )
            
            logger.info(f"  Generated: {len(orders)} orders, {len(page_views)} page views, {len(inventory)} inventory changes")
            
            # Save to database or publish to message queue
            if output_format == "database":
                # Direct database insert (TODO: implement)
                pass
            else:
                # Publish to Redpanda/Kafka
                if self.producer:
                    self._publish_events(orders, page_views, inventory)
        
        logger.info("Historical data generation completed")
    
    def _publish_events(self, orders, page_views, inventory):
        """Helper method to publish events to Redpanda"""
        if not self.producer:
            return
        
        # Convert entities to dicts and publish
        order_events = [self._order_to_dict(order) for order in orders]
        page_view_events = [self._page_view_to_dict(pv) for pv in page_views]
        inventory_events = [self._inventory_to_dict(inv) for inv in inventory]
        
        # Publish in batches (use project settings from config.py)
        if order_events:
            self.producer.publish_batch(
                settings.KAFKA_TOPIC_ORDERS,
                order_events,
                key_extractor=lambda e: e.get('order_id')
            )
        
        if page_view_events:
            self.producer.publish_batch(
                settings.KAFKA_TOPIC_PAGE_VIEWS,
                page_view_events,
                key_extractor=lambda e: e.get('user_id')
            )
        
        if inventory_events:
            self.producer.publish_batch(
                settings.KAFKA_TOPIC_INVENTORY,
                inventory_events,
                key_extractor=lambda e: e.get('product_id')
            )
        
        logger.info(
            f"Published: {len(order_events)} orders, "
            f"{len(page_view_events)} page views, "
            f"{len(inventory_events)} inventory changes"
        )
    
    def _order_to_dict(self, order):
        """Convert Order entity to dict"""
        return {
            'order_id': order.order_id,
            'user_id': order.user_id,
            'product_id': order.product_id,
            'timestamp': order.timestamp.isoformat(),
            'amount': order.amount,
            'status': order.status.value,
            'quantity': order.quantity
        }
    
    def _page_view_to_dict(self, page_view):
        """Convert PageView entity to dict"""
        return {
            'view_id': page_view.view_id,
            'user_id': page_view.user_id,
            'product_id': page_view.product_id,
            'timestamp': page_view.timestamp.isoformat(),
            'session_id': page_view.session_id,
            'page_url': page_view.page_url,
            'duration_seconds': page_view.duration_seconds
        }
    
    def _inventory_to_dict(self, inventory):
        """Convert Inventory entity to dict"""
        return {
            'product_id': inventory.product_id,
            'timestamp': inventory.timestamp.isoformat(),
            'stock_change': inventory.stock_change,
            'current_stock': inventory.current_stock,
            'warehouse_id': inventory.warehouse_id
        }


if __name__ == "__main__":
    # Example usage
    config = GeneratorConfig(
        orders_per_second=0.5,
        page_views_per_second=5.0,
        total_users=1000,
        total_products=500
    )
    
    # Initialize producer with project settings
    try:
        producer = RedpandaProducer(settings=settings)
        logger.info("Connected to Redpanda")
    except Exception as e:
        logger.warning(f"Failed to connect to Redpanda: {e}")
        logger.warning("Running in dry-run mode (no publishing)")
        producer = None
    
    generator = DataGenerator(config, producer=producer)
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "historical":
            # Generate historical data
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            generator.generate_historical_batch(days=days, output_format="events")
        else:
            # Generate real-time stream
            duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
            generator.generate_and_publish_stream(duration_seconds=duration)
    finally:
        if producer:
            producer.close()

