# Data Platform Foundation

Shared infrastructure for all data platform projects.

## What's Included

- **PostgreSQL** - Data warehouse (port 5433)
- **Redpanda** - Message queue/Kafka-compatible streaming (port 19092)
- **Redis** - Caching layer (port 6379)
- **Redpanda Console** - Web UI for monitoring topics (http://localhost:8080)

## Quick Start

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## How Projects Use This

Each project uses the same infrastructure but with isolated namespaces:

- **PostgreSQL**: Each project creates its own database (e.g., `ecommerce`, `iot`, `finance`)
- **Redpanda**: Each project uses prefixed topics (e.g., `ecommerce_orders`, `iot_sensors`)
- **Redis**: Each project uses prefixed keys (e.g., `ecommerce:user:123`, `iot:device:456`)

This allows multiple projects to run simultaneously without conflicts.

## Access Services

- PostgreSQL: `localhost:5433`
- Redpanda Kafka API: `localhost:19092`
- Redpanda Console: http://localhost:8080
- Redis: `localhost:6379`

