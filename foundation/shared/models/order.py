"""
Order data model - represents an e-commerce order
"""

from dataclasses import dataclass
from datetime import datetime

# from typing import Dict, Any, List
from enum import Enum


class OrderStatus(str, Enum):
    """Order status enumeration"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class Order:
    """Order data model"""

    order_id: str
    user_id: str
    product_id: str
    timestamp: datetime
    amount: float
    status: OrderStatus
    quantity: int = 1

    def __post_init__(self):
        """Validate order entity"""
        if self.amount < 0:
            raise ValueError("Order amount cannot be negative")
        if self.quantity < 1:
            raise ValueError("Order quantity must be at least 1")
