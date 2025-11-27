"""
Page View data model - represents a user page view event
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PageView:
    """Page view data model"""
    view_id: str
    user_id: str
    product_id: Optional[str]
    timestamp: datetime
    session_id: str
    page_url: str
    duration_seconds: Optional[float] = None
    
    def __post_init__(self):
        """Validate page view entity"""
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise ValueError("Duration cannot be negative")

