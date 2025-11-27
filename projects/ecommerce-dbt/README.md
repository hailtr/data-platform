# E-commerce Analytics with dbt

**Focused Project: E-commerce Real-Time Analytics**

This project demonstrates end-to-end e-commerce data analytics using dbt for data transformations.

## What This Project Shows

- **Data Engineering**: Real-time event streaming (Redpanda/Kafka)
- **Data Modeling**: Star schema design and dbt transformations
- **SQL Skills**: Complex analytics queries and transformations
- **Business Intelligence**: E-commerce metrics and KPIs

## Architecture

```
Data Generator → Redpanda (ecommerce_* topics) → Ingestion → PostgreSQL (ecommerce DB) → dbt → Analytics
```

## Quick Start

### Prerequisites

1. Start foundation infrastructure:
   ```bash
   cd ../../foundation
   docker-compose up -d
   ```

2. Initialize database:
   ```bash
   python projects/ecommerce-dbt/scripts/init_database.py
   ```
   Or from the project directory:
   ```bash
   cd projects/ecommerce-dbt
   python scripts/init_database.py
   ```

3. Generate data:
   ```bash
   python projects/ecommerce-dbt/data_generator/main.py 60
   ```

4. Run ingestion (in a separate terminal):
   ```bash
   python projects/ecommerce-dbt/ingestion/main.py
   ```
   This will start all three ingestion pipelines (orders, page views, inventory).

5. Run dbt transformations:
   ```bash
   cd projects/ecommerce-dbt/dbt
   dbt run
   ```
   
   To run specific models:
   ```bash
   dbt run --select staging    # Run staging models only
   dbt run --select marts      # Run mart models only
   dbt test                     # Run data quality tests
   ```

## Project Structure

```
ecommerce-dbt/
├── data_generator/     # Synthetic e-commerce event generator
├── ingestion/          # Kafka consumer → PostgreSQL pipeline
│   ├── kafka_consumer.py  # Ingestion pipeline classes
│   └── main.py            # Main ingestion runner
├── storage/            # Database schemas and migrations
├── dbt/                # dbt models and transformations
│   ├── models/
│   │   ├── staging/    # Staging models (clean operational data)
│   │   ├── intermediate/ # Intermediate transformations
│   │   └── marts/      # Final analytical tables
│   │       ├── facts/  # Fact tables
│   │       ├── dimensions/ # Dimension tables
│   │       └── aggregates/ # Aggregated metrics
│   ├── dbt_project.yml # dbt project configuration
│   └── profiles.yml     # Database connection profiles
├── scripts/
│   └── init_database.py # Database initialization script
└── config.py          # Project-specific configuration
```

## Key Features

- **Real-time event streaming**: Orders, page views, inventory changes
- **Data warehouse**: PostgreSQL with star schema
- **dbt transformations**: Analytics-ready models
- **Business metrics**: Revenue, conversion rates, customer analytics

## Data Model

### Operational Tables (PostgreSQL)
- `orders` - Order transactions
- `page_views` - Page view events
- `inventory_changes` - Inventory change events
- `users` - User dimension
- `products` - Product dimension

### Analytical Tables (dbt)
- **Staging**: `stg_orders`, `stg_page_views`, `stg_inventory_changes`, `stg_users`, `stg_products`
- **Dimensions**: `dim_users`, `dim_products`, `dim_time`
- **Facts**: `fct_orders`, `fct_page_views`
- **Aggregates**: `agg_daily_sales`, `agg_user_behavior`

## Next Steps

- [x] Complete ingestion pipeline (write to PostgreSQL)
- [x] Add dbt models for analytics
- [ ] Create Power BI dashboard
- [ ] Add data quality tests
- [ ] Add dbt documentation

