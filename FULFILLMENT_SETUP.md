# Autonomous Fulfillment System Setup

## Overview

The cs-os platform now runs a fully autonomous, asynchronous portfolio fulfillment pipeline:

```
Stripe Webhook (checkout.session.completed)
    ↓
[FAST] Provision Client + Enqueue Job (< 100ms)
    ↓
[ASYNC] Worker polls PortfolioBuildJob table
    ↓
Step 1: PROVISIONING → Step 2: GENERATING → Step 3: PUSHING → Step 4: NOTIFYING
    ↓
Complete: Portfolio live, client notified
```

### Key Features

- **Asynchronous**: Webhook returns immediately; no 20–30s blocking
- **Idempotent**: Every step can be retried safely without side effects
- **Self-healing**: Automatic retries with exponential backoff
- **Scalable**: Handles 200+ concurrent orders without human intervention
- **Observable**: Full job state machine tracking via API

---

## Required Environment Variables

### Core Infrastructure

```bash
DATABASE_URL=sqlite:///./cs_os.db
# or: postgresql://user:pass@localhost/cs_os
# or: mysql://user:pass@localhost/cs_os
```

### Stripe Integration

```bash
STRIPE_SECRET_KEY=sk_test_...            # Stripe secret key (test or live)
STRIPE_WEBHOOK_SECRET=whsec_...          # Stripe webhook signing secret
STRIPE_PRICE_FOUNDATION=price_...        # Product price ID
STRIPE_PRICE_LAUNCH=price_...            # Product price ID
STRIPE_PRICE_ACCELERATOR=price_...       # Product price ID
```

### GitHub Integration (for portfolio repo creation & deployment)

```bash
GITHUB_TOKEN=ghp_...                     # GitHub personal access token
GITHUB_ORG=your-github-org               # Organization to create repos in

# GitHub token should have these scopes:
#  - repo (full control of private repositories)
#  - workflow (read/write GitHub Actions)
```

### LLM Integration (for portfolio generation)

Choose one:

**Anthropic Claude:**
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

**Google Gemini:**
```bash
GOOGLE_API_KEY=AIza...
```

### Email Delivery (for client notifications)

Choose one:

**Resend (recommended for Vercel projects):**
```bash
EMAIL_PROVIDER=resend
RESEND_API_KEY=re_...
EMAIL_FROM=noreply@yourdomain.com
EMAIL_FROM_NAME="Your Site Name"
```

**SendGrid:**
```bash
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG....
EMAIL_FROM=noreply@yourdomain.com
```

**SMTP (self-hosted):**
```bash
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-password
SMTP_USE_TLS=true
EMAIL_FROM=noreply@yourdomain.com
```

### Application Configuration

```bash
BASE_URL=http://localhost:8000          # Public base URL (for email links)
OPS_PASSWORD=your-secure-password       # Admin dashboard access
INTAKE_TOKEN_PEPPER=random-secret       # For token encryption
```

---

## Running the System

### 1. Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app.database import engine; from app.migrations import run_migrations; run_migrations(engine)"

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start worker
python -m app.worker
```

### 2. Production Deployment (Vercel)

The webhook endpoint automatically enqueues jobs. To process them, run the worker as a background job:

**Option A: Vercel Cron Job (simple, for low volume)**
```bash
# In vercel.json
{
  "crons": [
    {
      "path": "/api/worker/run",
      "schedule": "*/5 * * * *"  // Every 5 minutes
    }
  ]
}
```

**Option B: Separate Worker Service (recommended for 200+ orders/day)**

Create a lightweight worker container or Lambda function:

```python
# app/worker.py is the entry point
# Run: python -m app.worker --poll-interval 5 --batch-size 10

# Docker example:
# FROM python:3.11-slim
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install -r requirements.txt
# COPY app/ app/
# CMD ["python", "-m", "app.worker"]
```

Deploy as:
- AWS ECS task (set DATABASE_URL, API keys via secrets)
- Google Cloud Run (same)
- Railway background worker (same)
- systemd service on your own server

**Option C: Inngest (serverless, auto-scaling) [Future Enhancement]**

```python
# app/jobs/portfolio_build.py
from inngest import Inngest

inngest = Inngest(app_id="cs-os", api_key=os.environ["INNGEST_API_KEY"])

@inngest.create_function(fn_id="portfolio.build")
async def build_portfolio(event):
    # process_job(job_id)
    pass
```

This requires minimal code changes; all retry/scaling is managed by Inngest.

---

## API Endpoints

### Check Build Status

```bash
# By Stripe session ID (from checkout)
GET /builds/status?session_id=cs_123abc

# By client ID
GET /builds/status?client_id=42

# By job ID
GET /builds/123

# Response:
{
  "status": "complete",
  "current_step": null,
  "portfolio_url": "https://portfolio-xyz.vercel.app",
  "github_repo_url": "https://github.com/your-org/portfolio-xyz",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:35:42Z",
  "notified_client_at": "2024-01-15T10:35:43Z"
}
```

### List All Builds

```bash
GET /builds/list?limit=20&offset=0&status=complete

# Response:
{
  "total": 45,
  "limit": 20,
  "offset": 0,
  "jobs": [...]
}
```

---

## Job State Machine

```
PENDING
  ↓
PROVISIONING (prepare repo, fetch client credentials)
  ↓
GENERATING (call LLM with client intake data)
  ↓
PUSHING (commit to GitHub, trigger Vercel)
  ↓
NOTIFYING (send client their live portfolio URL)
  ↓
COMPLETE

--- OR on failure ---

Any step → RETRY_PENDING (wait, then retry)
  ↓ (after max_retries exceeded)
  ↓
FAILED (with error_message and error_step logged)
```

### Idempotency Guarantees

- **PROVISIONING**: Checks if GitHub repo already created; skips if exists
- **GENERATING**: Regenerates portfolio (safe; no side effects)
- **PUSHING**: Checks if commit already pushed; retrieves live URL from git history
- **NOTIFYING**: Checks if email already sent (notified_client_at); skips if true

This means workers can be restarted, jobs can be manually retried, and duplicate execution is always safe.

---

## Monitoring & Debugging

### Check Worker Status

```bash
# Logs go to stdout/stderr; in production, aggregate with:
#  - CloudWatch (AWS)
#  - Stackdriver (GCP)
#  - Datadog / New Relic / Sentry

# Key log lines:
# - "Starting job 123"
# - "Completed job 123"
# - "[provisioning] Failed to provision repo: ..."
```

### Manual Job Retry

```python
from app.database import get_db
from app.fulfillment_orchestrator import process_job

db = next(get_db())
job_id = 123
process_job(db, job_id)  # Retries from current step
```

### Check Job Details

```bash
# Via API
curl http://localhost:8000/builds/123

# Via database
SELECT * FROM portfolio_build_jobs WHERE id = 123;
```

---

## Scaling for 200+ Concurrent Orders

### Bottleneck 1: Database

- Use PostgreSQL or MySQL (not SQLite for production)
- Add connection pooling (pgBouncer for Postgres)
- Index on: `portfolio_build_jobs.status`, `portfolio_build_jobs.created_at`

### Bottleneck 2: Worker Processing

- **Single worker**: ~5–10 jobs/minute (assuming 30s per job)
- **For 200 concurrent orders**: Run 20–40 workers in parallel
- Use job queue with auto-scaling (Inngest, AWS SQS + Lambda, etc.)

### Bottleneck 3: LLM Concurrency

- Anthropic/Google APIs have rate limits
- Add queue of LLM calls with backoff
- Consider batching or streaming for better throughput

### Bottleneck 4: GitHub API Rate Limits

- GitHub: 5000 requests/hour (authenticated)
- Create ~1 request per portfolio (minimal impact)
- If needed, shard repos across multiple org accounts

---

## Rollback Plan

If the worker crashes or a job fails:

1. **Job stays in RETRY_PENDING**: Next worker run will pick it up
2. **Manual retry**: Call `process_job(db, job_id)` from any Python script
3. **Database backup**: Jobs table is immutable audit log; you can always rewind

To pause fulfillment without code changes:
```sql
-- Stop accepting new jobs
UPDATE portfolio_build_jobs SET status = 'failed' WHERE status = 'pending';

-- Or just don't run the worker
# Stop the worker container/process
```

---

## Next Steps

1. Set all required environment variables (see above)
2. Run database migrations: `python -c "from app.database import engine; from app.migrations import run_migrations; run_migrations(engine)"`
3. Test webhook locally: `curl -X POST http://localhost:8000/webhooks/stripe ...`
4. Start worker: `python -m app.worker`
5. Verify jobs are processing: `curl http://localhost:8000/builds/1`

For production, deploy worker as separate service and monitor logs.
