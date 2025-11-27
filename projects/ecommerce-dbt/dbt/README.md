# E-commerce dbt Project

This dbt project transforms operational e-commerce data into an analytical star schema.

## Project Structure

```
dbt/
├── models/
│   ├── staging/          # Clean operational data
│   ├── intermediate/     # Transformations
│   └── marts/           # Final analytical tables
│       ├── facts/       # Fact tables
│       ├── dimensions/  # Dimension tables
│       └── aggregates/  # Aggregated metrics
├── dbt_project.yml      # Project configuration
└── profiles.yml         # Database connection profiles
```

## Models

### Staging Models
- `stg_orders` - Cleaned order data
- `stg_page_views` - Cleaned page view data
- `stg_inventory_changes` - Cleaned inventory change data
- `stg_users` - Cleaned user data
- `stg_products` - Cleaned product data

### Dimension Models
- `dim_users` - User dimension
- `dim_products` - Product dimension
- `dim_time` - Time dimension

### Fact Models
- `fct_orders` - Order facts
- `fct_page_views` - Page view facts

### Aggregate Models
- `agg_daily_sales` - Daily sales metrics
- `agg_user_behavior` - User behavior metrics

## Usage

1. Install dbt dependencies:
   ```bash
   dbt deps
   ```

2. Run all models:
   ```bash
   dbt run
   ```

3. Run specific models:
   ```bash
   dbt run --select staging
   dbt run --select marts
   ```

4. Test models:
   ```bash
   dbt test
   ```

5. Generate documentation:
   ```bash
   dbt docs generate
   dbt docs serve
   ```

## Database Connection

The project connects to PostgreSQL at `localhost:5433` using the `ecommerce` database. Connection details are configured in `profiles.yml`.


