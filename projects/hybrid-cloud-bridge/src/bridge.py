"""
Hybrid Cloud Bridge - Streams events from Redpanda to GCS as Parquet files
Uses foundation/shared components for consistency
"""

import os
import sys
import tempfile
from datetime import datetime
from typing import Any, List

import pandas as pd
from loguru import logger

# Add foundation to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from foundation.shared.config.settings import Settings
from foundation.shared.messaging import RedpandaConsumer, BatchProcessor
from foundation.shared.storage import GCSClient


class BridgeSettings(Settings):
    """Bridge-specific settings extending foundation"""
    GCS_BUCKET_NAME: str = ""
    GCS_PROJECT_ID: str = ""
    BATCH_SIZE: int = 5000
    BATCH_TIMEOUT_SECONDS: int = 60

    class Config:
        env_file = ".env"


class ParquetBatchProcessor(BatchProcessor):
    """Processes batches by writing to Parquet and uploading to GCS"""

    def __init__(self, gcs_client: GCSClient, settings: BridgeSettings):
        super().__init__(
            batch_size=settings.BATCH_SIZE,
            batch_timeout_seconds=settings.BATCH_TIMEOUT_SECONDS,
        )
        self.gcs_client = gcs_client

    def _process_batch(self, batch: List[Any]) -> bool:
        """Convert batch to Parquet and upload to GCS"""
        df = pd.DataFrame(batch)

        # Generate paths
        now = datetime.utcnow()
        date_str = now.strftime("%Y-%m-%d")
        timestamp_str = now.strftime("%H-%M-%S-%f")
        blob_path = f"raw/{date_str}/{timestamp_str}.parquet"

        # Write to temp file
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
            tmp_path = tmp.name
            df.to_parquet(tmp_path, compression="snappy", index=False)

        # Upload with retry
        success = self.gcs_client.upload_file(
            source_path=tmp_path,
            destination_blob=blob_path,
            content_type="application/octet-stream",
        )

        # Cleanup
        os.remove(tmp_path)
        return success


def main():
    settings = BridgeSettings()
    logger.info("Starting Hybrid Cloud Bridge")

    gcs = GCSClient(settings=settings)
    processor = ParquetBatchProcessor(gcs_client=gcs, settings=settings)

    consumer = RedpandaConsumer(
        topics=["events-stream"],
        group_id="bridge-group",
        enable_auto_commit=False,  # Manual commit after successful flush
        settings=settings,
    )

    def handle_message(value, key, partition, offset):
        flushed = processor.add(value)
        if flushed:
            consumer.commit()
            logger.debug(f"Committed offset {offset}")

    try:
        consumer.consume(handler=handle_message)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        # Flush remaining buffer before exit
        if processor.buffer_size > 0:
            logger.info(f"Flushing remaining {processor.buffer_size} items")
            if processor.flush():
                consumer.commit()
        consumer.close()


if __name__ == "__main__":
    main()
