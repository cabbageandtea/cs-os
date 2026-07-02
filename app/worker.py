"""Background worker: processes portfolio build jobs asynchronously.

This is a simple polling worker designed to run as a background process
or long-lived task. It continuously fetches pending jobs and processes them.

For production scale (200+ concurrent orders), consider:
- Moving to Inngest (serverless queue with auto-scaling)
- Using AWS SQS + Lambda
- Using Google Cloud Tasks
- Running multiple worker instances with load balancing

Design principles:
- Processes one job at a time (can parallelize with multiprocessing)
- Idempotent: safe to restart at any time
- Graceful shutdown: finishes current job before stopping
- Logging: all steps logged for debugging and audit trail
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys
import time
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.fulfillment_orchestrator import (
    OrchestrationError,
    get_pending_jobs,
    process_job,
)

logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
_should_shutdown = False


def _setup_signal_handlers() -> None:
    """Register SIGTERM/SIGINT handlers for graceful shutdown."""
    def handle_signal(signum, frame):
        global _should_shutdown
        logger.info("Received signal %s, shutting down gracefully...", signum)
        _should_shutdown = True

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)


@contextmanager
def get_db_session(engine) -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def process_single_job(db: Session, job_id: int) -> bool:
    """
    Process a single job. Returns True if successful, False if retriable error.
    
    Implements atomic job lock to prevent concurrent processing of same job by multiple workers.
    Catches all exceptions to ensure worker doesn't crash.
    """
    from app.models import PortfolioBuildJob
    from sqlalchemy import update
    
    try:
        # Atomic lock: only process if we can transition from PENDING/RETRY_PENDING to PROVISIONING
        # This prevents race conditions where two workers grab same job
        job = db.get(PortfolioBuildJob, job_id, with_for_update=True)
        
        if not job:
            logger.error("Job %s not found", job_id)
            return False
        
        # Double-check job is still pending after acquiring lock
        if job.status not in ("pending", "retry_pending"):
            logger.debug("Job %s already processed (status=%s)", job_id, job.status)
            return True
        
        logger.info("Processing job %s (status=%s, retry=%d/%d)", job_id, job.status, job.retry_count, job.max_retries)
        process_job(db, job_id)
        logger.info("Completed job %s", job_id)
        return True
    except OrchestrationError as exc:
        logger.error("Orchestration error in job %s: %s", job_id, exc, exc_info=True)
        # Job has been updated with error state; worker continues
        return False
    except Exception as exc:
        logger.exception("Unexpected error processing job %s: %s", job_id, exc)
        # Don't crash; log and continue
        return False


def run_worker(poll_interval: int = 5, batch_size: int = 10, max_jobs: int = 0) -> None:
    """
    Run the background worker loop.
    
    Args:
        poll_interval: Seconds between job fetches (default 5)
        batch_size: Number of jobs to fetch per poll (default 10)
        max_jobs: Max jobs to process before exiting (0 = infinite)
    """
    _setup_signal_handlers()

    # Get database URL from environment
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set; cannot start worker")
        sys.exit(1)

    engine = create_engine(database_url, echo=False)
    jobs_processed = 0

    logger.info("Worker starting with poll_interval=%s, batch_size=%s", poll_interval, batch_size)

    try:
        while not _should_shutdown:
            with get_db_session(engine) as db:
                # Fetch pending jobs
                pending_jobs = get_pending_jobs(db, limit=batch_size)
                
                if not pending_jobs:
                    # No jobs; wait and retry
                    logger.debug("No pending jobs, waiting %s seconds...", poll_interval)
                    time.sleep(poll_interval)
                    continue

                logger.info("Found %d pending jobs", len(pending_jobs))

                # Process each job
                for job in pending_jobs:
                    if _should_shutdown:
                        logger.info("Shutdown requested, stopping job processing")
                        break

                    job_id = job.id
                    
                    # RETRY_PENDING jobs: check if backoff delay has passed
                    if job.status == "retry_pending" and job.retry_count > 0:
                        backoff_seconds = min(2 ** (job.retry_count + 1), 300)
                        time_since_update = (time.time() - job.updated_at.timestamp()) if job.updated_at else 0
                        if time_since_update < backoff_seconds:
                            logger.debug(f"Job {job_id} backoff in progress ({time_since_update:.1f}s / {backoff_seconds}s), skipping")
                            continue
                    
                    process_single_job(db, job_id)
                    jobs_processed += 1

                    # Stop if max_jobs reached
                    if max_jobs > 0 and jobs_processed >= max_jobs:
                        logger.info("Reached max_jobs=%s, exiting", max_jobs)
                        _should_shutdown = True
                        break

    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
    except Exception as exc:
        logger.exception("Worker crashed: %s", exc)
        sys.exit(1)
    finally:
        engine.dispose()
        logger.info("Worker stopped. Processed %d jobs total.", jobs_processed)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    run_worker()
