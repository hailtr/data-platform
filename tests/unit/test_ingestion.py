import pytest
from unittest.mock import MagicMock, call, patch
from datetime import datetime
from ingestion.kafka_consumer import OrdersIngestionPipeline

class TestOrdersIngestionPipeline:
    
    @pytest.fixture
    def pipeline(self):
        return OrdersIngestionPipeline(batch_size=2)

    def test_process_order_adds_to_batch(self, pipeline, mock_redpanda_consumer):
        # Setup
        pipeline.start() # Initialize consumer
        
        # Simulate processing
        order_data = {
            "order_id": "ord_1",
            "user_id": "user_1",
            "product_id": "prod_1",
            "timestamp": "2023-01-01T12:00:00Z",
            "amount": 100.0,
            "status": "completed",
            "quantity": 1
        }
        
        # Access the handler passed to consume
        handler = mock_redpanda_consumer.consume.call_args[1]['handler']
        handler(order_data, None, 0, 0)
        
        assert len(pipeline.batch) == 1
        assert pipeline.batch[0] == order_data

    def test_batch_insertion_trigger(self, pipeline, mock_redpanda_consumer, mock_db_connection):
        mock_conn, mock_cursor = mock_db_connection
        pipeline.start()
        
        handler = mock_redpanda_consumer.consume.call_args[1]['handler']
        
        # Add 2 items (batch size is 2)
        order1 = {
            "order_id": "ord_1", 
            "user_id": "u1", 
            "product_id": "p1", 
            "timestamp": "2023-01-01T12:00:00Z", 
            "amount": 10.0, 
            "status": "new",
            "quantity": 1
        }
        order2 = {
            "order_id": "ord_2", 
            "user_id": "u2", 
            "product_id": "p2", 
            "timestamp": "2023-01-01T12:01:00Z", 
            "amount": 20.0, 
            "status": "new",
            "quantity": 2
        }
        
        handler(order1, None, 0, 0)
        assert len(pipeline.batch) == 1
        assert mock_cursor.executemany.call_count == 0
        
        handler(order2, None, 0, 1)
        assert len(pipeline.batch) == 0 # Batch should be cleared
        assert mock_cursor.executemany.call_count == 1

    def test_insert_batch_error_handling(self, pipeline, mock_redpanda_consumer, mock_db_connection):
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.executemany.side_effect = Exception("DB Error")
        
        pipeline.batch = [{
            "order_id": "ord_1",
            "user_id": "user_1",
            "product_id": "prod_1",
            "timestamp": "2023-01-01T12:00:00Z",
            "amount": 100.0,
            "status": "completed",
            "quantity": 1
        }]
        
        # Mock time.sleep to avoid waiting during retries
        with patch("time.sleep") as mock_sleep:
            with pytest.raises(Exception):
                pipeline._insert_batch()
            
            # Verify it retried 3 times (so sleep called 3 times)
            assert mock_sleep.call_count == 3
            assert mock_cursor.executemany.called
            
        assert len(pipeline.batch) == 1 # Batch should NOT be cleared on error (so it can be retried)
