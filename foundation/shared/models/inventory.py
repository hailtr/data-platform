"""
Inventory data model - represents inventory changes
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Inventory:
    """Inventory data model"""
    product_id: str
    timestamp: datetime
    stock_change: int
    current_stock: int
    warehouse_id: Optional[str] = None
    
    def __post_init__(self):
        """Validate inventory entity"""
        if self.current_stock < 0:
            raise ValueError("Current stock cannot be negative")

