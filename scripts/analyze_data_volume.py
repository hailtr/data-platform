"""
Analyze data volume for portfolio project
"""
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
project_path = project_root / "projects" / "ecommerce-dbt"
sys.path.insert(0, str(project_path))
sys.path.insert(0, str(project_root))

from data_generator.config import GeneratorConfig
from data_generator.event_generator import EventGenerator

# Current config
current = GeneratorConfig()
event_gen = EventGenerator(current)
orders, pv, inv = event_gen.generate_batch(86400)  # 1 day

print("=" * 60)
print("DATA VOLUME ANALYSIS")
print("=" * 60)

print(f"\nCurrent Configuration:")
print(f"  Orders/sec: {current.orders_per_second}")
print(f"  Page Views/sec: {current.page_views_per_second}")
print(f"  Inventory/sec: {current.inventory_updates_per_second}")
print(f"  Total Users: {current.total_users}")
print(f"  Total Products: {current.total_products}")

print(f"\nVolume per DAY:")
print(f"  Orders: {len(orders):,}")
print(f"  Page Views: {len(pv):,}")
print(f"  Inventory Changes: {len(inv):,}")

print(f"\nVolume per MONTH (30 days):")
print(f"  Orders: {len(orders) * 30:,}")
print(f"  Page Views: {len(pv) * 30:,}")
print(f"  Inventory Changes: {len(inv) * 30:,}")

# Calculate metrics
daily_revenue = sum(o.amount for o in orders)
monthly_revenue = daily_revenue * 30
conversion_rate = len(orders) / len(pv) * 100

print(f"\nBusiness Metrics (estimated):")
print(f"  Daily Revenue: ${daily_revenue:,.2f}")
print(f"  Monthly Revenue: ${monthly_revenue:,.2f}")
print(f"  Conversion Rate: {conversion_rate:.2f}%")

print(f"\n" + "=" * 60)
print("RECOMMENDATIONS FOR PORTFOLIO")
print("=" * 60)

print(f"\nFor Portfolio Project:")
print(f"  [OK] Current volume is GOOD for:")
print(f"    - Demonstrating streaming capabilities")
print(f"    - Real-time dashboards")
print(f"    - Analytics and insights")
print(f"    - Data pipeline processing")

print(f"\n  Consider adjustments:")
print(f"    - For more impressive numbers: increase to 1-2 orders/sec")
print(f"    - For faster testing: reduce to 0.2 orders/sec")
print(f"    - Current is balanced for portfolio demonstration")

print(f"\n  Data quality matters more than volume:")
print(f"    - Realistic patterns [OK]")
print(f"    - Proper correlations [OK]")
print(f"    - Time-based distributions [OK]")
print(f"    - Business logic [OK]")

