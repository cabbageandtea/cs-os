# Autonomous Fulfillment System: Deployment Checklist

## Pre-Deployment Verification

### Code Quality
- [x] All Python files syntax-validated
- [x] Imports verified (fulfillment_orchestrator, worker, routes/fulfillment)
- [x] Models created (PortfolioBuildJob, PortfolioBuildJobStatus)
- [x] Webhook modified to enqueue jobs
- [x] Email service integrated
- [x] Routes registered in main.py

### Documentation
- [x] FULFILLMENT_SETUP.md (env vars, deployment guide)
- [x] ARCHITECTURE.md (system design, scaling, security)
- [x] FULFILLMENT_IMPLEMENTATION.md (files created, testing)
- [x] DEPLOYMENT_CHECKLIST.md (this file)

---

## Phase 1: Local Development Setup

### 1.1 Environment Variables
Create `.env` file with:
```bash
DATABASE_URL=sqlite:///./cs_os.db

STRIPE_SECRET_KEY=sk_test_YOUR_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET
STRIPE_PRICE_FOUNDATION=price_foundation_test
STRIPE_PRICE_LAUNCH=price_launch_test
STRIPE_PRICE_ACCELERATOR=price_accelerator_test

GITHUB_TOKEN=ghp_YOUR_TOKEN  # (test with dummy for now)
GITHUB_ORG=your-org

ANTHROPIC_API_KEY=sk-ant-YOUR_KEY  # (or GOOGLE_API_KEY)

EMAIL_PROVIDER=resend
RESEND_API_KEY=re_YOUR_KEY  # (or SMTP_HOST/SENDGRID_API_KEY)

BASE_URL=http://localhost:8000
OPS_PASSWORD=dev-password
INTAKE_TOKEN_PEPPER=dev-pepper-key
```

**Checklist:**
- [ ] Copy example from FULFILLMENT_SETUP.md
- [ ] Set Stripe keys from dashboard
- [ ] Set GitHub token (or use placeholder)
- [ ] Set LLM API key
- [ ] Set email provider credentials

### 1.2 Database Initialization
```bash
# Create tables
python -c "from app.database import engine; from app.migrations import run_migrations; run_migrations(engine)"
```

**Checklist:**
- [ ] Database file created at DATABASE_URL location
- [ ] All tables exist (check `sqlite3 cs_os.db ".tables"`)
- [ ] portfolio_build_jobs table present

### 1.3 Local Run
```bash
# Terminal 1: Start FastAPI
uvicorn app.main:app --reload

# Terminal 2: Start worker
python -m app.worker --poll-interval 5 --batch-size 10
```

**Checklist:**
- [ ] FastAPI starts without errors (http://localhost:8000)
- [ ] /health endpoint responds
- [ ] Worker starts and shows "Worker starting with poll_interval=5"
- [ ] No import errors in either process

### 1.4 Test Enqueuing
```python
# In Python REPL
from app.database import get_db
from app.fulfillment_orchestrator import create_build_job, get_pending_jobs

db = next(get_db())
job = create_build_job(db, client_id=1, purchase_id=1)
print(f"Created job {job.id}")

pending = get_pending_jobs(db, limit=10)
print(f"Pending jobs: {len(pending)}")
```

**Checklist:**
- [ ] Job created in database
- [ ] Job appears in pending_jobs query
- [ ] Job status is "pending"

### 1.5 Test Job Processing
```bash
# In running worker terminal, observe:
# "Starting job 1"
# "[provisioning] Failed to provision repo: ..." (expected; no GitHub token yet)
```

**Checklist:**
- [ ] Worker picks up the job
- [ ] Job transitions to "retry_pending" (after failure)
- [ ] No worker crashes

### 1.6 Test API Status Endpoint
```bash
curl http://localhost:8000/builds/1
# Expected: job status JSON with current_step, retry_count, etc.
```

**Checklist:**
- [ ] Returns HTTP 200
- [ ] JSON includes: status, current_step, error_message, created_at

---

## Phase 2: Implementation (Stubs → Real Code)

### 2.1 LLM Integration
Implement `app/portfolio_generator.py`:

```python
async def generate_portfolio_html(client: Client, package_slug: str) -> str:
    from anthropic import Anthropic
    # OR: from google.generativeai import ...
    
    # Call LLM with client data
    # Return HTML
```

**Checklist:**
- [ ] API key works (test with simple call)
- [ ] Returns valid HTML string
- [ ] Handles errors gracefully (raises GenerationError)

**Test:**
```bash
# Update job to move past retry
UPDATE portfolio_build_jobs SET status='provisioning', current_step='provisioning' WHERE id=1;

# Run worker again
python -m app.worker --max-jobs 1

# Expect: Job progresses to GENERATING step
```

### 2.2 GitHub Integration
Implement `app/github_integration.py`:

```python
def push_portfolio_to_github(client: Client, portfolio_html: str) -> tuple[str, str]:
    from github import Github
    
    # Create repo (or get existing)
    # Commit portfolio_html to index.html
    # Trigger Vercel deployment
    # Return (github_url, vercel_live_url)
```

**Checklist:**
- [ ] GitHub API token works
- [ ] Can create repos in GITHUB_ORG
- [ ] Handles duplicate repos (idempotent)
- [ ] Vercel deployment triggered
- [ ] Returns live URL after deploy

**Test:**
```bash
# Set job status to PUSHING
UPDATE portfolio_build_jobs SET status='pushing', current_step='pushing' WHERE id=1;

# Run worker
python -m app.worker --max-jobs 1

# Expect: Repo created on GitHub, deployed to Vercel
```

### 2.3 Email Template (Optional)
Customize `app/email_service.py` send_portfolio_live_email function:

**Checklist:**
- [ ] Email preview looks good
- [ ] Links are correct
- [ ] Sender/subject is branded

**Test:**
```bash
# Set job status to NOTIFYING
UPDATE portfolio_build_jobs SET status='notifying', current_step='notifying', portfolio_url='https://example.com' WHERE id=1;

# Run worker
python -m app.worker --max-jobs 1

# Check email inbox (or logs if using dev mode)
```

---

## Phase 3: Integration Testing

### 3.1 End-to-End Test (No Real Payment)
```bash
# Create purchase and client manually
INSERT INTO purchases (stripe_session_id, stripe_payment_intent_id, package_slug, amount, status, customer_email)
VALUES ('test_session_1', 'pi_test_1', 'launch', 9900, 'paid', 'test@example.com');

# Trigger webhook handler
from app.provisioning import provision_client_from_purchase
from app.stripe_webhook import _enqueue_portfolio_build

db = next(get_db())
purchase = db.get(Purchase, 1)
provision_client_from_purchase(db, purchase, customer_email='test@example.com', stripe_customer_id=None, stripe_payment_intent_id='pi_test_1')
_enqueue_portfolio_build(db, purchase)

# Run worker to process
python -m app.worker --max-jobs 1
```

**Checklist:**
- [ ] Job created
- [ ] Provisioning step completes
- [ ] Generation step calls LLM
- [ ] GitHub push completes
- [ ] Email sent
- [ ] Job status = "complete"

### 3.2 Webhook Test (Real Stripe Data)
If you have a test Stripe account:

```bash
# Listen for webhooks locally
ngrok http 8000

# Configure Stripe to send to ngrok URL
# Complete a test purchase

# Verify:
# - Webhook received in FastAPI logs
# - Job created in database
# - Worker picks up job
# - Job completes successfully
```

**Checklist:**
- [ ] Webhook signature validates
- [ ] Client created
- [ ] Job created
- [ ] Worker processes without error

### 3.3 Failure Recovery Test
```bash
# Simulate worker crash mid-job
# Kill worker process while job is running

# Restart worker
python -m app.worker

# Verify: Job continues from last step (idempotent)
```

**Checklist:**
- [ ] Job status not lost
- [ ] No duplicate GitHub commits
- [ ] No duplicate emails sent
- [ ] Job recovers and completes

---

## Phase 4: Production Deployment

### 4.1 Production Database
- [ ] Migrate from SQLite to PostgreSQL (or MySQL)
- [ ] Set DATABASE_URL to production database
- [ ] Run migrations on production database
- [ ] Verify all tables created
- [ ] Add indexes:
  ```sql
  CREATE INDEX idx_job_status ON portfolio_build_jobs(status);
  CREATE INDEX idx_job_created ON portfolio_build_jobs(created_at);
  CREATE INDEX idx_job_client ON portfolio_build_jobs(client_id);
  ```

### 4.2 FastAPI Server Deployment (Vercel/Production)
- [ ] Set all environment variables in production
- [ ] Deploy FastAPI to production URL
- [ ] Test /health endpoint
- [ ] Configure Stripe webhook to point to production /webhooks/stripe endpoint
- [ ] Test webhook delivery from Stripe dashboard

### 4.3 Worker Deployment (Separate Service)
**Option A: ECS (AWS)**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ app/
CMD ["python", "-m", "app.worker", "--poll-interval", "5", "--batch-size", "20"]
```

**Option B: Cloud Run (GCP)**
```bash
gcloud run deploy cs-os-worker \
  --source . \
  --platform managed \
  --memory 512Mi \
  --set-env-vars DATABASE_URL=$DATABASE_URL,STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY,...
```

**Option C: Railway/Render**
- [ ] Create new service with `python -m app.worker`
- [ ] Set environment variables via dashboard
- [ ] Enable auto-restart on crash

**Checklist:**
- [ ] Worker process starts without errors
- [ ] Can connect to production database
- [ ] Logs visible in platform's logging
- [ ] Worker picks up jobs from queue

### 4.4 Monitoring & Observability
- [ ] Set up logging aggregation (Datadog, CloudWatch, Sentry)
- [ ] Create alarms for:
  - Failed jobs (status='failed')
  - Stuck jobs (status='*' and created_at > 1 hour ago)
  - Worker crashes (exit code != 0)
- [ ] Set up dashboard with key metrics:
  - Jobs completed per minute
  - P95 job latency
  - Error rate
  - Queue depth

### 4.5 Backup & Recovery
- [ ] Database daily backups configured
- [ ] Test recovery procedure
- [ ] Document runbook for failed jobs:
  ```sql
  -- Resume failed job
  UPDATE portfolio_build_jobs SET status='retry_pending', retry_count=0 WHERE id=123;
  -- Next worker run will retry
  ```

### 4.6 Load Testing
```bash
# Simulate 200 concurrent orders
# Create 200 jobs in database
for i in {1..200}; do
  INSERT INTO portfolio_build_jobs (client_id, purchase_id, status) 
  VALUES ($i, $i, 'pending');
done

# Start worker and measure:
# - Time to process all 200
# - CPU/memory usage
# - Database connection pool status
```

**Checklist:**
- [ ] All 200 jobs complete
- [ ] No connection pool exhaustion
- [ ] Worker doesn't crash under load
- [ ] Database doesn't run out of disk space

---

## Phase 5: Launch & Monitoring

### 5.1 Pre-Launch Checks
- [ ] All env vars set and tested
- [ ] Database backups automated
- [ ] Worker auto-restart configured
- [ ] Monitoring/alerting active
- [ ] Runbook written and shared with team

### 5.2 Launch Day
- [ ] Deploy to production (all components)
- [ ] Monitor logs continuously for 2 hours
- [ ] Process first 10 test orders manually
- [ ] Verify jobs complete end-to-end
- [ ] Check email delivery
- [ ] Verify GitHub repos created
- [ ] Test Vercel deployments

### 5.3 Day 1 Post-Launch
- [ ] Monitor job success rate (target: 99%+)
- [ ] Check for any failed jobs
- [ ] Monitor worker CPU/memory usage
- [ ] Review error logs for patterns

### 5.4 Week 1 Post-Launch
- [ ] Analyze metrics (throughput, latency, errors)
- [ ] Document any issues and resolutions
- [ ] Optimize poll interval / batch size based on load
- [ ] Plan upgrade to Inngest if needed

---

## Known Limitations & Mitigations

### Limitation 1: Sequential Job Processing
**Issue:** Single worker processes one job at a time (~30s each).

**Mitigation:** Run multiple workers in parallel.

**Future:** Upgrade to Inngest for auto-scaling.

### Limitation 2: LLM Rate Limits
**Issue:** Anthropic/Google APIs have rate limits.

**Mitigation:** Add queue of LLM calls with backoff.

**Future:** Implement streaming or batching.

### Limitation 3: GitHub Token Storage
**Issue:** Client's GitHub token stored in database.

**Mitigation:** Encrypt at rest with field-level encryption.

**Future:** Use OAuth2 flow instead of direct token.

---

## Troubleshooting

### Job Stuck in PROVISIONING
```sql
SELECT * FROM portfolio_build_jobs WHERE id=123;
-- Check error_message and error_step
-- If safe to retry:
UPDATE portfolio_build_jobs SET status='retry_pending', retry_count=0 WHERE id=123;
```

### Worker Not Processing Jobs
```bash
# Check worker logs
tail -f /var/log/cs-os-worker.log

# Check job queue
SELECT COUNT(*) FROM portfolio_build_jobs WHERE status IN ('pending', 'retry_pending');

# Restart worker
systemctl restart cs-os-worker
```

### Email Not Sending
```bash
# Verify email provider API key works
# Test send via API:
curl -X POST https://api.resend.com/emails \
  -H "Authorization: Bearer $RESEND_API_KEY" \
  -d '{"from":"test@example.com",...}'

# Check email service logs
```

### GitHub Deployment Failing
```bash
# Verify GitHub token has correct scopes
# Test API call:
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos

# Check repo creation permissions
```

---

## Sign-Off

Once all phases complete:

- [ ] Co-founder / PM: Code reviewed & approved
- [ ] DevOps: Infrastructure setup & tested
- [ ] QA: End-to-end testing complete
- [ ] Support: Runbook reviewed & understood

**Launch Date:** ________________

**Launch Status:** 🟢 Ready / 🟡 Partial / 🔴 Not Ready

---

## References

- FULFILLMENT_SETUP.md: Environment variables and deployment
- ARCHITECTURE.md: System design and scaling
- FULFILLMENT_IMPLEMENTATION.md: Files created and testing procedures
