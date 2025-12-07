# Data Platform Portfolio

**Multi-Project Data Engineering Portfolio** by Rafael Ortiz

A production-ready data engineering portfolio showcasing real-world data platform patterns, built on a shared infrastructure foundation with fully-functional end-to-end projects.

---

## 🎯 Portfolio Structure

```
data-platform/
├── foundation/              # Shared infrastructure (Docker services)
│   ├── docker-compose.yml   # PostgreSQL, Redpanda, Redis
│   └── shared/             # Reusable libraries (messaging, database, models)
│
├── projects/                # Self-contained data engineering projects
│   ├── ecommerce-dbt/       # ✅ E-commerce analytics with dbt (COMPLETE)
│   ├── iot-powerbi/         # 🔜 IoT real-time dashboard (planned)
│   └── finance-tableau/     # 🔜 Financial analytics pipeline (planned)
│
├── scripts/                 # Utility scripts for testing and verification
└── tests/                   # Integration tests
```

---

## 🏗️ Foundation

**Shared Infrastructure** - Containerized services used by all projects

| Service | Purpose | Port | Web UI |
|---------|---------|------|--------|
| **PostgreSQL** | Data warehouse | 5433 | - |
| **Redpanda** | Kafka-compatible streaming | 19092 | [Console](http://localhost:8080) |
| **Redis** | Caching layer | 6379 | - |

### Multi-Tenant Design
Each project uses the same infrastructure with **namespace isolation**:
- ✅ Separate PostgreSQL databases per project
- ✅ Prefixed Kafka topics per project (`ecommerce_*`, `iot_*`, etc.)
- ✅ Prefixed Redis keys per project

📖 See [`foundation/README.md`](foundation/README.md) for architecture details.

---

## 📊 Projects

### 1. ✅ Hybrid Cloud Marketplace Platform (BigQuery + dbt)
> **Focus**: Enterprise Data Warehouse, Advanced Analytics, Self-Healing Pipelines

**What it demonstrates:**
- ✅ **Medallion Architecture**: Bronze (Ext), Silver (Staging), Gold (Marts).
- ✅ **Self-Healing Data**: Automated backfill of corrupt country codes using Window Functions.
- ✅ **Marketplace Analytics**: Integrated Revenue Model (Retail Sales + Ad Revenue).
- ✅ **Advanced Logic**: 
    - **Funnel Analysis**: Conversion rates (View -> Click -> Purchase).
    - **Bot Detection**: Automated flagging of high-frequency sessions (>50 events/min).
    - **Regional Pricing**: PPP adjustments for Tier 2 markets.

**Tech Stack**: BigQuery, dbt, Python, GCS (Parquet)

### 2. ✅ E-commerce Real-Time Stream (Local)
> **Focus**: Real-time event streaming, SQL transformations

**Tech Stack**: Redpanda (Kafka), PostgreSQL, dbt, Python, Docker

**Status**: Fully functional end-to-end pipeline ready for demo

📖 [View Project Details →](projects/ecommerce-dbt/README.md)

### 2. 🔜 IoT Real-time Dashboard (Planned)

> **Focus**: Real-time streaming analytics, Power BI dashboards

- IoT sensor data streaming
- Real-time analytics and aggregations
- Power BI live visualizations
- Monitoring dashboards

**Tech Stack**: Redpanda, PostgreSQL, Power BI, Python

### 3. 🔜 Financial Analytics Pipeline (Planned)

> **Focus**: Batch ETL processing, Tableau visualizations

- Financial transaction processing
- Batch ETL pipelines with SCD Type 2
- Tableau dashboards
- Regulatory reporting

**Tech Stack**: Redpanda, PostgreSQL, Tableau, Python

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Docker Desktop installed and running
- Python 3.10+ with venv
- Git

### Start the E-commerce Analytics Demo

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd data-platform

# 2. Start infrastructure (PostgreSQL, Redpanda, Redis)
cd foundation
docker-compose up -d
cd ..

# 3. Set up Python environment
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt

# 4. Initialize the database
python scripts\init_database.py

# 5. Run the quality checks (optional)
scripts\run_checks.bat
```

🎉 **That's it!** Your data platform is ready. See the [E-commerce project README](projects/ecommerce-dbt/README.md) for running the full demo.

### Quick Verification

```bash
# Check that all services are running
python scripts\check_services.py

# Access Redpanda Console
start http://localhost:8080
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
- **Enterprise Warehousing**: Google BigQuery, Partitioning, External Tables
- **Advanced dbt**: Custom Macros, Incremental Models, Snapshotting
- **Marketplace Analytics**: ROAS, Funnel Optimization, Bot Mitigation
- **Visualization**: Power BI, Tableau, Looker Studio
- **SQL Analytics**: Window Functions, Complex Joins, CTEs

### Software Engineering
- Modular architecture
- Code reusability (OOP Design Patterns)
- Resilience patterns (DLQ, Retries)
- Configuration management
- Testing and validation

---

## Getting Started

1. **Clone the repository**
2. **Start foundation**: `cd foundation && docker-compose up -d`
3. **Choose a project**: Navigate to `projects/[project-name]`
4. **Follow project README**: Each project has specific instructions

---

## 🛠️ Development & Quality

### Quality Checks

Run comprehensive checks before committing:

```bash
# Windows
scripts\run_checks.bat

# macOS/Linux
chmod +x scripts/run_checks.sh && ./scripts/run_checks.sh
```

**What it tests:**
- ✅ **Black**: Code formatting
- ✅ **Flake8**: Linting and style
- ✅ **Pytest**: Unit and integration tests

### Pre-commit Hook (Recommended)

Automate quality checks on every commit:

```bash
# Windows (PowerShell)
@"
#!/bin/sh
scripts/run_checks.bat
"@ | Out-File -FilePath .git/hooks/pre-commit -Encoding ASCII

# macOS/Linux
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/sh
./scripts/run_checks.sh
EOF
chmod +x .git/hooks/pre-commit
```

---

## Contributing

This is a portfolio project. Each project is self-contained and can be run independently.

---

## License

MIT

---

**Built for learning and demonstrating data engineering skills**
