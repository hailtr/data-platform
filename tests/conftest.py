import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch

# Add project roots to path
PROJECT_ROOT = Path(__file__).parent.parent
FOUNDATION_PATH = PROJECT_ROOT / "foundation"
ECOMMERCE_PATH = PROJECT_ROOT / "projects" / "ecommerce-dbt"

sys.path.insert(0, str(FOUNDATION_PATH))
sys.path.insert(0, str(ECOMMERCE_PATH))


@pytest.fixture
def mock_settings():
    with patch("config.settings") as mock:
        mock.KAFKA_TOPIC_ORDERS = "ecommerce_orders"
        mock.KAFKA_TOPIC_PAGE_VIEWS = "ecommerce_page_views"
        mock.KAFKA_TOPIC_INVENTORY = "ecommerce_inventory"
        mock.POSTGRES_HOST = "localhost"
        mock.POSTGRES_PORT = 5432
        mock.POSTGRES_USER = "test"
        mock.POSTGRES_PASSWORD = "test"
        mock.POSTGRES_DB = "test_db"
        yield mock


@pytest.fixture
def mock_db_connection():
    with patch("ingestion.kafka_consumer.get_db_connection") as mock_ctx:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_ctx.return_value.__enter__.return_value = mock_conn
        yield mock_conn, mock_cursor


@pytest.fixture
def mock_redpanda_consumer():
    with patch("ingestion.base.RedpandaConsumer") as mock:
        consumer_instance = MagicMock()
        mock.return_value = consumer_instance
        yield consumer_instance
