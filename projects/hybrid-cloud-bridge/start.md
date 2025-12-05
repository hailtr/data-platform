# PROJECT BLUEPRINT: Hybrid Cloud Bridge (Stream-to-Lakehouse)

## 1. Context & Objective
We are building a cost-optimized, hybrid data pipeline that bridges a local high-throughput streaming source (Redpanda) with a cloud data warehouse (Google BigQuery).
The goal is to avoid expensive streaming inserts by implementing a **Micro-batching** strategy: buffering events locally, compressing them into Parquet, and uploading them to Google Cloud Storage (GCS) for querying via BigQuery External Tables.

## 2. Tech Stack
- **Language:** Python 3.11
- **Streaming Source:** Redpanda (Kafka-compatible) running in Docker.
- **Infrastructure as Code:** Terraform (GCP Provider).
- **Cloud Storage:** Google Cloud Storage (GCS) - Standard class.
- **Warehouse:** Google BigQuery (External Tables).
- **Containerization:** Docker & Docker Compose.
- **Libraries:** `kafka-python`, `pandas`, `pyarrow` (for Parquet), `google-cloud-storage`.

## 3. Architecture Logic
1.  **Ingest:** Listen to a Redpanda topic (`events-stream`).
2.  **Buffer:** Accumulate messages in an in-memory list.
3.  **Trigger:** Flush the buffer when EITHER:
    - `BATCH_SIZE` reaches 5,000 records.
    - `BATCH_TIMEOUT` reaches 60 seconds.
4.  **Process:** Convert list to Pandas DataFrame -> Write to local Parquet file (Snappy compression).
5.  **Upload:** Upload Parquet file to GCS Bucket (`gs://{bucket_name}/raw/{date}/{timestamp}.parquet`).
6.  **Cleanup:** Delete local file and reset buffer.

## 4. Directory Structure
Generate the project using this structure:
.
├── infra/                  # Terraform code
│   ├── main.tf            # GCS Bucket, BQ Dataset, Service Account
│   ├── variables.tf
│   └── outputs.tf
├── src/                    # Python Application
│   ├── bridge.py          # Main consumer loop & batching logic
│   ├── gcp_client.py      # Wrapper for GCS upload
│   └── requirements.txt
├── docker-compose.yml      # Redpanda + Python App
├── .env                    # Environment variables (GCP_CREDENTIALS, BUCKET_NAME)
└── .gitignore

## 5. Implementation Steps (Execution Plan)

### Step 1: Infrastructure (Terraform)
Create the Terraform configuration in `infra/` to provision:
- A GCS Bucket (Private).
- A BigQuery Dataset (`analytics_raw`).
- A Service Account with `Storage Object Admin` and `BigQuery User` roles.
- Output the Service Account Key (we will use this for local dev).

### Step 2: Docker Environment
Create a `docker-compose.yml` that spins up a single-node **Redpanda** cluster.
Add a `producer_mock.py` script (temporary) to generate dummy JSON events into Redpanda for testing.

### Step 3: The Bridge Logic (Python)
Develop `src/bridge.py`. It must implement the Batching Logic described in Section 3.
- *Constraint:* Use `try/except` blocks to handle network failures during upload (don't lose data).
- *Constraint:* Use Environment Variables for configuration.

### Step 4: Dockerization
Create a `Dockerfile` for the Python app and add it to `docker-compose.yml`. Ensure credentials can be mounted or passed safely.

## 6. Definition of Done
The project is complete when:
1.  We can run `terraform apply` to create cloud resources.
2.  We run `docker-compose up`.
3.  We see Parquet files appearing in the GCS Bucket.
4.  We can run a SQL query in BigQuery console (`SELECT * FROM ...`) and see the data.