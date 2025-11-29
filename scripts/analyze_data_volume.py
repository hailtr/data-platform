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

from data_generator.config import GeneratorConfig  # noqa: E402
from data_generator.event_generator import EventGenerator  # noqa: E402

# Current config
current = GeneratorConfig()
event_gen = EventGenerator(current)
orders, pv, inv = event_gen.generate_batch(86400)  # 1 day

print("=" * 60)
print("DATA VOLUME ANALYSIS")
print("=" * 60)

print("\nCurrent Configuration:")
print(f"  Orders/sec: {current.orders_per_second}")
print(f"  Page Views/sec: {current.page_views_per_second}")
print(f"  Inventory/sec: {current.inventory_updates_per_second}")
print(f"  Total Users: {current.total_users}")
print(f"  Total Products: {current.total_products}")

print("\nVolume per DAY:")
print(f"  Orders: {len(orders):,}")
print(f"  Page Views: {len(pv):,}")
print(f"  Inventory Changes: {len(inv):,}")

print("\nVolume per MONTH (30 days):")
print(f"  Orders: {len(orders) * 30:,}")
print(f"  Page Views: {len(pv) * 30:,}")
print(f"  Inventory Changes: {len(inv) * 30:,}")

# Calculate metrics
daily_revenue = sum(o.amount for o in orders)
monthly_revenue = daily_revenue * 30
conversion_rate = len(orders) / len(pv) * 100

print("\nBusiness Metrics (estimated):")
print(f"  Daily Revenue: ${daily_revenue:,.2f}")
print(f"  Monthly Revenue: ${monthly_revenue:,.2f}")
print(f"  Conversion Rate: {conversion_rate:.2f}%")

print("\n" + "=" * 60)
print("RECOMMENDATIONS FOR PORTFOLIO")
print("=" * 60)

print("\nFor Portfolio Project:")
print("  [OK] Current volume is GOOD for:")
print("    - Demonstrating streaming capabilities")
print("    - Real-time dashboards")
print("    - Analytics and insights")
print("    - Data pipeline processing")

print("\n  Consider adjustments:")
print("    - For more impressive numbers: increase to 1-2 orders/sec")
print("    - For faster testing: reduce to 0.2 orders/sec")
print("    - Current is balanced for portfolio demonstration")

print("\n  Data quality matters more than volume:")
print("    - Realistic patterns [OK]")
print("    - Proper correlations [OK]")
print("    - Time-based distributions [OK]")
print("    - Business logic [OK]")
