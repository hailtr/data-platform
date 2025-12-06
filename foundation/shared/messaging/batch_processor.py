"""Generic batch processor for micro-batching patterns"""

import time
from abc import ABC, abstractmethod
from typing import Any, List, Optional
from loguru import logger


class BatchProcessor(ABC):
    """Abstract batch processor with size and time-based flush triggers"""

    def __init__(
        self,
        batch_size: int = 5000,
        batch_timeout_seconds: int = 60,
    ):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout_seconds
        self._buffer: List[Any] = []
        self._last_flush_time = time.time()

    def add(self, item: Any) -> bool:
        """Add item to buffer. Returns True if flush was triggered."""
        self._buffer.append(item)
        if self._should_flush():
            return self.flush()
        return False

    def _should_flush(self) -> bool:
        """Check if flush should be triggered"""
        if len(self._buffer) >= self.batch_size:
            return True
        if time.time() - self._last_flush_time >= self.batch_timeout:
            return True
        return False

    def flush(self) -> bool:
        """Flush buffer using subclass implementation"""
        if not self._buffer:
            return True

        batch = self._buffer.copy()
        logger.info(f"Flushing batch of {len(batch)} items")

        try:
            success = self._process_batch(batch)
            if success:
                self._buffer.clear()
                self._last_flush_time = time.time()
                logger.info("Batch flush successful")
            return success
        except Exception as e:
            logger.error(f"Batch flush failed: {e}")
            return False

    @abstractmethod
    def _process_batch(self, batch: List[Any]) -> bool:
        """Subclass implements actual batch processing logic"""
        pass

    @property
    def buffer_size(self) -> int:
        return len(self._buffer)
