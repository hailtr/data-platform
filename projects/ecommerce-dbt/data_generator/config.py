"""
Configuration for data generator
"""

from dataclasses import dataclass
from typing import List


@dataclass
class GeneratorConfig:
    """Configuration for synthetic data generation"""

    # Generation rates (events per second)
    orders_per_second: float = 0.5  # ~30 orders/minute
    page_views_per_second: float = 5.0  # ~300 page views/minute
    inventory_updates_per_second: float = 0.1  # ~6 updates/minute

    # User base
    total_users: int = 1000
    active_users_per_day: int = 200

    # Product catalog
    total_products: int = 500
    categories: List[str] = None

    # Business hours pattern (higher activity during business hours)
    business_hours_multiplier: float = 2.0

    # Conversion rate (page views → orders)
    conversion_rate: float = 0.03  # 3% conversion rate

    def __post_init__(self):
        if self.categories is None:
            self.categories = [
                "Electronics",
                "Clothing",
                "Home & Garden",
                "Sports",
                "Books",
                "Toys",
                "Beauty",
                "Food",
            ]
