"""
E-commerce project configuration
Uses namespace isolation: ecommerce database and ecommerce_* topics
"""
from pydantic_settings import BaseSettings
from typing import Optional


class EcommerceSettings(BaseSettings):
    """E-commerce project settings with namespace isolation"""
    
    # Database - uses 'ecommerce' database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5433
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "ecommerce"  # Project-specific database
    
    # Redis - uses 'ecommerce:' prefix
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PREFIX: str = "ecommerce:"  # Namespace prefix
    
    # Kafka/Redpanda - uses 'ecommerce_*' topic prefix
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:19092"
    KAFKA_TOPIC_ORDERS: str = "ecommerce_orders"
    KAFKA_TOPIC_PAGE_VIEWS: str = "ecommerce_page_views"
    KAFKA_TOPIC_INVENTORY: str = "ecommerce_inventory"
    
    # DuckDB (Data Warehouse)
    DUCKDB_PATH: str = "data/ecommerce_warehouse.duckdb"
    
    # Application
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Project-specific settings instance
settings = EcommerceSettings()

