# Data Platform Portfolio

**Multi-Project Data Engineering Portfolio**

A collection of focused data engineering projects built on a shared infrastructure foundation, demonstrating real-world data platform patterns and analytics tools.

---

## Portfolio Structure

```
data-platform-portfolio/
├── foundation/              # Shared infrastructure (Docker, services)
│   ├── docker-compose.yml   # PostgreSQL, Redpanda, Redis
│   └── shared/             # Reusable code (messaging, database, models)
│
└── projects/                # Focused projects
    ├── ecommerce-dbt/       # E-commerce analytics with dbt
    ├── iot-powerbi/         # IoT real-time dashboard (coming soon)
    └── finance-tableau/     # Financial analytics pipeline (coming soon)
```

---

## Foundation

**Shared Infrastructure** - Used by all projects

- **PostgreSQL** - Data warehouse (port 5433)
- **Redpanda** - Kafka-compatible message queue (port 19092)
- **Redis** - Caching layer (port 6379)
- **Redpanda Console** - Web UI for monitoring (http://localhost:8080)

Each project uses the same infrastructure with **namespace isolation**:
- Different PostgreSQL databases per project
- Prefixed Kafka topics per project
- Prefixed Redis keys per project

See [foundation/README.md](foundation/README.md) for details.

---

## Projects

### 1. E-commerce Analytics with dbt

**Focus**: Data modeling, SQL transformations, dbt

- Real-time e-commerce event streaming
- Star schema data warehouse
- dbt transformations for analytics
- Business metrics and KPIs

**Tech Stack**: Redpanda, PostgreSQL, dbt, Python

[View Project →](projects/ecommerce-dbt/README.md)

### 2. IoT Real-time Dashboard (Coming Soon)

**Focus**: Real-time streaming, Power BI dashboards

- IoT sensor data streaming
- Real-time analytics
- Power BI visualizations
- Live monitoring dashboards

**Tech Stack**: Redpanda, PostgreSQL, Power BI, Python

### 3. Financial Analytics Pipeline (Coming Soon)

**Focus**: Batch processing, Tableau visualizations

- Financial transaction processing
- Batch ETL pipelines
- Tableau dashboards
- Regulatory reporting

**Tech Stack**: Redpanda, PostgreSQL, Tableau, Python

---

## Quick Start

### 1. Start Foundation Infrastructure

```bash
cd foundation
docker-compose up -d
```

### 2. Run a Project

Each project has its own README with specific instructions. For example:

```bash
cd projects/ecommerce-dbt
# Follow project-specific README
```

---

## Why This Structure?

### For Recruiters

- **Clear Focus**: Each project demonstrates specific skills
- **Easy to Navigate**: Understand each project in 2-5 minutes
- **Shows Versatility**: Different tools, different domains
- **Professional**: Intentional, well-organized

### For Me

- **Reusable Code**: Foundation used by all projects
- **Easy to Maintain**: Update foundation once, all projects benefit
- **Scalable**: Easy to add new projects
- **Portfolio-Ready**: Each project tells a clear story

---

## Skills Demonstrated

### Infrastructure & Architecture
- Docker containerization
- Multi-tenant data platform design
- Namespace isolation patterns
- Infrastructure as Code (Docker Compose)

### Data Engineering
- Real-time event streaming (Kafka/Redpanda)
- Data ingestion pipelines
- Data warehousing (PostgreSQL)
- ETL/ELT patterns

### Analytics & BI
- dbt data transformations
- Power BI dashboards
- Tableau visualizations
- SQL analytics

### Software Engineering
- Modular architecture
- Code reusability
- Configuration management
- Testing and validation

---

## Getting Started

1. **Clone the repository**
2. **Start foundation**: `cd foundation && docker-compose up -d`
3. **Choose a project**: Navigate to `projects/[project-name]`
4. **Follow project README**: Each project has specific instructions

---

## Local Development

### Quality Checks
Run the following script before pushing changes to ensure code quality:
```bash
scripts/run_checks.bat
```
This will run Black (formatting), Flake8 (linting), and Pytest (tests).

### Pre-commit Hook (Optional)
To automate this, you can create a git pre-commit hook:
1. Create `.git/hooks/pre-commit`
2. Add:
   ```bash
   #!/bin/sh
   ./scripts/run_checks.bat
   ```
3. Make it executable (`chmod +x .git/hooks/pre-commit`)

---

## Contributing

This is a portfolio project. Each project is self-contained and can be run independently.

---

## License

MIT

---

**Built for learning and demonstrating data engineering skills**
