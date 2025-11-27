"""
Main ingestion pipeline runner
Runs all ingestion pipelines concurrently
"""
import signal
import sys
from pathlib import Path
from threading import Thread
from loguru import logger

# Add foundation to path
project_root = Path(__file__).parent.parent.parent.parent
foundation_path = project_root / "foundation"
sys.path.insert(0, str(foundation_path))
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.kafka_consumer import (
    OrdersIngestionPipeline,
    PageViewsIngestionPipeline,
    InventoryIngestionPipeline
)

# Global pipeline instances
pipelines = []

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Shutting down ingestion pipelines...")
    for pipeline in pipelines:
        try:
            pipeline.stop()
        except Exception as e:
            logger.error(f"Error stopping pipeline: {e}")
    sys.exit(0)

def run_pipeline(pipeline_class, name: str):
    """Run a single pipeline in a thread"""
    try:
        pipeline = pipeline_class()
        pipelines.append(pipeline)
        logger.info(f"Starting {name} pipeline...")
        pipeline.start()
    except Exception as e:
        logger.error(f"Error in {name} pipeline: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting ecommerce ingestion pipelines...")
    
    # Start pipelines in separate threads
    threads = [
        Thread(target=run_pipeline, args=(OrdersIngestionPipeline, "Orders"), daemon=True),
        Thread(target=run_pipeline, args=(PageViewsIngestionPipeline, "Page Views"), daemon=True),
        Thread(target=run_pipeline, args=(InventoryIngestionPipeline, "Inventory"), daemon=True),
    ]
    
    for thread in threads:
        thread.start()
    
    # Wait for all threads
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        signal_handler(None, None)


