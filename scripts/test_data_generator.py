"""
Test the synthetic data generator
"""
import sys
from pathlib import Path
from datetime import datetime

# Add project to path
project_root = Path(__file__).parent.parent
project_path = project_root / "projects" / "ecommerce-dbt"
sys.path.insert(0, str(project_path))
sys.path.insert(0, str(project_root))

from data_generator.config import GeneratorConfig
from data_generator.event_generator import EventGenerator
from data_generator.user_generator import UserGenerator
from data_generator.product_generator import ProductGenerator
from loguru import logger

logger.remove()  # Remove default handler
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}", level="INFO")


def test_user_generator():
    """Test user generation"""
    print("\n=== Testing User Generator ===")
    user_gen = UserGenerator(total_users=100)
    
    print(f"Generated {len(user_gen.users)} users")
    
    # Show sample users
    print("\nSample users:")
    for i, user in enumerate(user_gen.users[:5]):
        print(f"  {user.user_id}: {user.country}, {user.tier}, signed up {user.signup_date.date()}")
    
    # Test active users
    active = user_gen.get_active_users(10)
    print(f"\nActive users (weighted by tier): {len(active)}")
    tier_dist = {}
    for user in active:
        tier_dist[user.tier] = tier_dist.get(user.tier, 0) + 1
    print(f"  Tier distribution: {tier_dist}")


def test_product_generator():
    """Test product generation"""
    print("\n=== Testing Product Generator ===")
    product_gen = ProductGenerator(total_products=50)
    
    print(f"Generated {len(product_gen.products)} products")
    
    # Show sample products
    print("\nSample products:")
    for i, product in enumerate(product_gen.products[:5]):
        print(f"  {product.product_id}: {product.category}, ${product.price:.2f}, {product.supplier}")
    
    # Test category distribution
    category_dist = {}
    for product in product_gen.products:
        category_dist[product.category] = category_dist.get(product.category, 0) + 1
    print(f"\nCategory distribution: {category_dist}")
    
    # Test popular products
    popular = product_gen.get_popular_products(5)
    print(f"\nPopular products (weighted):")
    for product in popular:
        print(f"  {product.product_id}: {product.category}, ${product.price:.2f}")


def test_event_generator():
    """Test event generation"""
    print("\n=== Testing Event Generator ===")
    
    config = GeneratorConfig(
        orders_per_second=1.0,
        page_views_per_second=5.0,
        total_users=100,
        total_products=50
    )
    
    event_gen = EventGenerator(config)
    
    # Generate sample events
    print("\nGenerating sample events...")
    
    # Generate orders
    print("\n--- Orders ---")
    for i in range(3):
        order = event_gen.generate_order()
        print(f"  Order {i+1}:")
        print(f"    ID: {order.order_id}")
        print(f"    User: {order.user_id}")
        print(f"    Product: {order.product_id}")
        print(f"    Amount: ${order.amount:.2f} (qty: {order.quantity})")
        print(f"    Status: {order.status.value}")
        print(f"    Time: {order.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Generate page views
    print("\n--- Page Views ---")
    for i in range(3):
        page_view = event_gen.generate_page_view()
        print(f"  Page View {i+1}:")
        print(f"    ID: {page_view.view_id}")
        print(f"    User: {page_view.user_id}")
        print(f"    Session: {page_view.session_id}")
        print(f"    URL: {page_view.page_url}")
        print(f"    Product: {page_view.product_id or 'N/A'}")
        print(f"    Duration: {page_view.duration_seconds:.1f}s")
        print(f"    Time: {page_view.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Generate inventory changes
    print("\n--- Inventory Changes ---")
    for i in range(3):
        inventory = event_gen.generate_inventory_change()
        print(f"  Inventory Change {i+1}:")
        print(f"    Product: {inventory.product_id}")
        print(f"    Change: {inventory.stock_change:+d}")
        print(f"    Current Stock: {inventory.current_stock}")
        print(f"    Warehouse: {inventory.warehouse_id}")
        print(f"    Time: {inventory.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")


def test_batch_generation():
    """Test batch generation"""
    print("\n=== Testing Batch Generation ===")
    
    config = GeneratorConfig(
        orders_per_second=0.5,
        page_views_per_second=3.0,
        inventory_updates_per_second=0.1,
        total_users=100,
        total_products=50
    )
    
    event_gen = EventGenerator(config)
    
    print("Generating 10 seconds of events...")
    orders, page_views, inventory = event_gen.generate_batch(duration_seconds=10)
    
    print(f"\nResults:")
    print(f"  Orders: {len(orders)}")
    print(f"  Page Views: {len(page_views)}")
    print(f"  Inventory Changes: {len(inventory)}")
    
    if orders:
        print(f"\nFirst order: {orders[0].order_id} at {orders[0].timestamp.strftime('%H:%M:%S')}")
        print(f"Last order: {orders[-1].order_id} at {orders[-1].timestamp.strftime('%H:%M:%S')}")
    
    if page_views:
        print(f"\nFirst page view: {page_views[0].view_id} at {page_views[0].timestamp.strftime('%H:%M:%S')}")
        print(f"Last page view: {page_views[-1].view_id} at {page_views[-1].timestamp.strftime('%H:%M:%S')}")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Synthetic Data Generator")
    print("=" * 60)
    
    try:
        test_user_generator()
        test_product_generator()
        test_event_generator()
        test_batch_generation()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


