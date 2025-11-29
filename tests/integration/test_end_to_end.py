import pytest
import time
from datetime import datetime
from ingestion.kafka_consumer import OrdersIngestionPipeline
from shared.database import get_db_connection

@pytest.mark.integration
class TestEndToEnd:
    """
    Integration tests requiring running infrastructure (Redpanda, Postgres).
    These tests assume the foundation `docker-compose up` has been run.
    """
    
    @pytest.fixture
    def db_connection(self):
        """Verify DB connection is available"""
        try:
            with get_db_connection() as conn:
                yield conn
        except Exception as e:
            pytest.skip(f"Database not available: {e}")

    def test_redpanda_connection(self):
        """
        Test that we can connect to Redpanda.
        """
        from shared.messaging import RedpandaConsumer
        from config import settings
        
        try:
            # Try to initialize consumer - this checks connection
            consumer = RedpandaConsumer(
                topics=[settings.KAFKA_TOPIC_ORDERS],
                group_id="test_integration_group",
                settings=settings
            )
            consumer.close()
        except Exception as e:
             pytest.fail(f"Failed to connect to Redpanda: {e}")
             
    def test_database_insertion(self, db_connection):
        """Verify we can insert into the actual database"""
        pipeline = OrdersIngestionPipeline(batch_size=1)
        
        # Manually populate batch
        pipeline.batch = [{
            "order_id": "test_integration_1",
            "user_id": "test_user",
            "product_id": "test_prod",
            "timestamp": datetime.now().isoformat(),
            "amount": 99.99,
            "status": "test",
            "quantity": 1
        }]
        
        # Try to insert
        try:
            pipeline._insert_batch()
            
            # Verify insertion
            with db_connection.cursor() as cur:
                cur.execute("SELECT * FROM orders WHERE order_id = 'test_integration_1'")
                result = cur.fetchone()
                assert result is not None
                assert result[0] == "test_integration_1" # Assuming order_id is first col
                
                # Cleanup
                cur.execute("DELETE FROM orders WHERE order_id = 'test_integration_1'")
        except Exception as e:
            pytest.fail(f"Database insertion failed: {e}")
