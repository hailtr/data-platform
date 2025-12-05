"""Google Cloud Storage client with retry logic"""

import time
from typing import Optional, TYPE_CHECKING
from google.cloud import storage
from google.api_core import exceptions as gcp_exceptions
from loguru import logger

if TYPE_CHECKING:
    from shared.config.settings import Settings

try:
    from shared.config.settings import settings as default_settings
except ImportError:
    default_settings = None


class GCSClient:
    """GCS client with exponential backoff retry"""

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        settings: Optional["Settings"] = None,
        max_retries: int = 3,
    ):
        self.settings = settings or default_settings
        if not self.settings:
            raise ValueError("Settings required")

        self.bucket_name = bucket_name or self.settings.GCS_BUCKET_NAME
        self.max_retries = max_retries
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.bucket_name)
        logger.info(f"GCS client initialized for bucket: {self.bucket_name}")

    def upload_file(
        self,
        source_path: str,
        destination_blob: str,
        content_type: str = "application/octet-stream",
    ) -> bool:
        """Upload file with exponential backoff retry"""
        for attempt in range(self.max_retries):
            try:
                blob = self.bucket.blob(destination_blob)
                blob.upload_from_filename(source_path, content_type=content_type)
                logger.info(f"Uploaded {source_path} -> gs://{self.bucket_name}/{destination_blob}")
                return True
            except gcp_exceptions.GoogleAPIError as e:
                wait_time = 2 ** attempt
                logger.warning(f"Upload failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(wait_time)
        logger.error(f"Upload failed after {self.max_retries} attempts: {source_path}")
        return False
