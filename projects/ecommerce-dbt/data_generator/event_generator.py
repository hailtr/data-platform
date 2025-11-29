"""
Generate synthetic e-commerce events (orders, page views, inventory)
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict

# from dataclasses import asdict

from shared.models.order import Order, OrderStatus
from shared.models.page_view import PageView
from shared.models.inventory import Inventory

from data_generator.config import GeneratorConfig
from data_generator.user_generator import UserGenerator
from data_generator.product_generator import ProductGenerator


class EventGenerator:
    """Generate synthetic e-commerce events"""

    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.user_gen = UserGenerator(config.total_users)
        self.product_gen = ProductGenerator(config.total_products, config.categories)

        # Track state for realistic behavior
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        self.product_stock: Dict[str, int] = {}  # product_id -> current_stock

        # Initialize stock levels
        for product in self.product_gen.products:
            self.product_stock[product.product_id] = random.randint(50, 500)

    def generate_order(self, timestamp: Optional[datetime] = None) -> Order:
        """Generate a synthetic order"""
        if timestamp is None:
            timestamp = datetime.now()

        user = self.user_gen.get_random_user()
        product = self.product_gen.get_random_product()

        # Order amount based on product price and quantity
        quantity = random.choices(
            [1, 2, 3, 4, 5], weights=[0.6, 0.2, 0.1, 0.05, 0.05]  # Most orders are single item
        )[0]

        amount = round(product.price * quantity, 2)

        # Order status distribution
        status = random.choices(
            [
                OrderStatus.PENDING,
                OrderStatus.CONFIRMED,
                OrderStatus.SHIPPED,
                OrderStatus.DELIVERED,
                OrderStatus.CANCELLED,
            ],
            weights=[0.05, 0.15, 0.20, 0.55, 0.05],  # Most orders are delivered
        )[0]

        return Order(
            order_id=f"order_{uuid.uuid4().hex[:12]}",
            user_id=user.user_id,
            product_id=product.product_id,
            timestamp=timestamp,
            amount=amount,
            status=status,
            quantity=quantity,
        )

    def generate_page_view(
        self, timestamp: Optional[datetime] = None, user_id: Optional[str] = None
    ) -> PageView:
        """Generate a synthetic page view"""
        if timestamp is None:
            timestamp = datetime.now()

        if user_id is None:
            user = self.user_gen.get_random_user()
            user_id = user.user_id

        # Get or create session for user
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = f"session_{uuid.uuid4().hex[:12]}"

        session_id = self.user_sessions[user_id]

        # Page types: homepage, category, product, cart, checkout
        page_types = ["homepage", "category", "product", "cart", "checkout"]
        page_type = random.choices(
            page_types, weights=[0.3, 0.3, 0.3, 0.05, 0.05]  # Most views are browsing
        )[0]

        product_id = None
        if page_type in ["product", "cart", "checkout"]:
            # Popular products are viewed more
            product = self.product_gen.get_popular_products(1)[0]
            product_id = product.product_id

        # Generate page URL
        if page_type == "homepage":
            page_url = "/"
        elif page_type == "category":
            category = random.choice(self.config.categories)
            page_url = f"/category/{category.lower().replace(' ', '-')}"
        elif page_type == "product":
            page_url = f"/product/{product_id}"
        elif page_type == "cart":
            page_url = "/cart"
        else:  # checkout
            page_url = "/checkout"

        # Duration based on page type
        if page_type == "product":
            duration = random.uniform(10.0, 120.0)  # Users spend time on product pages
        elif page_type == "homepage":
            duration = random.uniform(5.0, 30.0)
        else:
            duration = random.uniform(2.0, 15.0)

        return PageView(
            view_id=f"view_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            product_id=product_id,
            timestamp=timestamp,
            session_id=session_id,
            page_url=page_url,
            duration_seconds=round(duration, 2),
        )

    def generate_inventory_change(self, timestamp: Optional[datetime] = None) -> Inventory:
        """Generate a synthetic inventory change"""
        if timestamp is None:
            timestamp = datetime.now()

        product = self.product_gen.get_random_product()
        product_id = product.product_id

        # Get current stock
        current_stock = self.product_stock.get(product_id, 100)

        # Stock changes: mostly small adjustments, occasional large restocks
        if random.random() < 0.1:  # 10% chance of large restock
            stock_change = random.randint(50, 200)
        else:  # 90% chance of small adjustment
            stock_change = random.randint(-20, 10)

        new_stock = max(0, current_stock + stock_change)
        self.product_stock[product_id] = new_stock

        return Inventory(
            product_id=product_id,
            timestamp=timestamp,
            stock_change=stock_change,
            current_stock=new_stock,
            warehouse_id=random.choice(["WH-001", "WH-002", "WH-003"]),
        )

    def generate_batch(
        self, duration_seconds: int = 60, start_time: Optional[datetime] = None
    ) -> tuple[List[Order], List[PageView], List[Inventory]]:
        """
        Generate a batch of events over a time period

        Returns:
            Tuple of (orders, page_views, inventory_changes)
        """
        if start_time is None:
            start_time = datetime.now()

        orders = []
        page_views = []
        inventory_changes = []

        # Calculate number of events
        num_orders = int(self.config.orders_per_second * duration_seconds)
        num_page_views = int(self.config.page_views_per_second * duration_seconds)
        num_inventory = int(self.config.inventory_updates_per_second * duration_seconds)

        # Generate events with timestamps distributed over the duration
        for i in range(num_orders):
            timestamp = start_time + timedelta(seconds=random.uniform(0, duration_seconds))
            orders.append(self.generate_order(timestamp))

        for i in range(num_page_views):
            timestamp = start_time + timedelta(seconds=random.uniform(0, duration_seconds))
            page_views.append(self.generate_page_view(timestamp))

        for i in range(num_inventory):
            timestamp = start_time + timedelta(seconds=random.uniform(0, duration_seconds))
            inventory_changes.append(self.generate_inventory_change(timestamp))

        # Sort by timestamp
        orders.sort(key=lambda x: x.timestamp)
        page_views.sort(key=lambda x: x.timestamp)
        inventory_changes.sort(key=lambda x: x.timestamp)

        return orders, page_views, inventory_changes
