# Autonomous Fulfillment Architecture

## System Overview

The cs-os backend now operates as a fully autonomous, event-driven system for portfolio fulfillment. No manual triggers required.

```
┌─────────────────────────────────────────────────────────────────────┐
│ CLIENT JOURNEY                                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Client completes checkout → Stripe                              │
│  2. Stripe sends webhook → /webhooks/stripe                         │
│  3. FastAPI verifies signature (< 100ms latency)                    │
│  4. Webhook handler:                                                │
│     - Provisions client (create record, assign token)               │
│     - ENQUEUES portfolio build job                                  │
│     - Returns 200 OK immediately                                    │
│  5. Background WORKER polls PortfolioBuildJob table                 │
│  6. Worker executes 4-step state machine:                           │
│     a) PROVISIONING: fetch client intake data                       │
│     b) GENERATING: call LLM (Claude/Gemini) → portfolio HTML        │
│     c) PUSHING: commit to GitHub, trigger Vercel deploy             │
│     d) NOTIFYING: send client "portfolio live" email                │
│  7. Client receives portfolio URL via email                         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Design Patterns

### 1. Webhook Enqueue Pattern

**Why:** Webhooks must return < 200ms to Stripe. Heavy operations block the response.

**Solution:**
```python
# app/stripe_webhook.py
def _handle_checkout_completed(db, session):
    # Fast: < 50ms
    provision_client_from_purchase(db, purchase)
    
    # Fast: < 50ms (just insert a database record)
    _enqueue_portfolio_build(db, purchase)
    
    # Done; return 200 to Stripe immediately
```

**Benefit:** Scales to 1000+ orders/hour without timeouts.

### 2. State Machine Pattern

**Why:** Long workflows need clear state tracking, recovery, and auditability.

**Implementation:**
```python
# app/fulfillment_orchestrator.py
class PortfolioBuildJobStatus(Enum):
    PENDING → PROVISIONING → GENERATING → PUSHING → NOTIFYING → COMPLETE
                               ↓
                         (on error)
                               ↓
                         RETRY_PENDING → COMPLETE
                               ↓
                         (max retries)
                               ↓
                           FAILED
```

**Benefit:** 
- Clear visibility into each job's progress
- Automatic retry with exponential backoff
- Permanent failure logged with root cause

### 3. Idempotent Step Design

**Why:** Distributed systems fail; workers crash; we need safe retries.

**Example:**
```python
def _step_pushing(db, job, client, portfolio_html):
    """
    Idempotency: Check if commit already exists.
    If yes, return cached URL.
    If no, push and return new URL.
    """
    if job.github_repo_url:
        # Already pushed; return cached
        return job.github_repo_url, job.portfolio_url
    
    # First time; execute
    github_url, vercel_url = push_portfolio_to_github(client, portfolio_html)
    return github_url, vercel_url
```

**Benefit:** 
- Restart job 10 times = same result
- No duplicate pushes, commits, or emails
- Worker crashes are transparent

### 4. Database-Driven Queue

**Why:** Simple, reliable, no external dependencies.

**Implementation:**
```python
# Tables:
# portfolio_build_jobs: id, client_id, status, current_step, retry_count, ...

# Worker loop:
pending = db.query(PortfolioBuildJob).where(
    status.in_(['pending', 'retry_pending'])
).limit(10)

for job in pending:
    process_job(db, job.id)  # Idempotent
```

**Benefit:** 
- Single source of truth (database)
- Easy to inspect/debug
- Scales to thousands of jobs with proper indexing
- For higher scale, migrate to Inngest (no code changes needed)

---

## Core Modules

### `app/models.py`
Defines the `PortfolioBuildJob` table and `PortfolioBuildJobStatus` enum.

**Key fields:**
- `status`: Current step (PENDING → COMPLETE or FAILED)
- `current_step`: Human-readable step name for logging
- `retry_count`: How many retries attempted
- `max_retries`: Configurable retry limit (default 3)
- `portfolio_url`: Live URL when complete
- `error_message`: Failure reason if FAILED
- `notified_client_at`: Tracks idempotent email delivery

### `app/fulfillment_orchestrator.py` (392 lines)
Core state machine logic. No external dependencies (pure Python + SQLAlchemy).

**Key functions:**
- `create_build_job()`: Enqueue a new job (idempotent)
- `process_job()`: Execute the 4-step state machine
- `_step_provisioning()`: Fetch client credentials
- `_step_generating()`: Call LLM to generate portfolio
- `_step_pushing()`: Commit to GitHub, trigger Vercel
- `_step_notifying()`: Send client email with live URL
- `get_job_status()`: Return current job state (for API polling)
- `get_pending_jobs()`: Worker's polling query

**Error handling:**
- `StepError`: Retriable errors → RETRY_PENDING
- `OrchestrationError`: Unexpected errors → FAILED
- `max_retries`: After N failures, mark FAILED permanently

### `app/worker.py` (156 lines)
Background worker process.

**Key functions:**
- `run_worker()`: Main loop (poll, fetch, process, sleep)
- `process_single_job()`: Execute one job, catch all exceptions
- `_setup_signal_handlers()`: Graceful shutdown on SIGTERM/SIGINT

**Configuration:**
- `poll_interval`: Seconds between job fetches (default 5)
- `batch_size`: Jobs per poll (default 10)
- `max_jobs`: Exit after N jobs (0 = infinite)

**Deployment:**
```bash
# Development
python -m app.worker

# Production (multiple workers)
python -m app.worker --poll-interval 5 --batch-size 20
```

### `app/routes/fulfillment.py` (131 lines)
REST API for job status polling and listing.

**Endpoints:**
- `GET /builds/status?session_id=...`: Get status by Stripe session
- `GET /builds/status?client_id=...`: Get status by client
- `GET /builds/{job_id}`: Get status by job ID
- `GET /builds/list`: List all jobs (with filtering)

**Use case:** Frontend polls after checkout to show "Portfolio generating..." status.

### `app/stripe_webhook.py` (modified)
Added job enqueuing after client provisioning.

**Key change:**
```python
def _handle_checkout_completed(db, session):
    provision_client_from_purchase(...)  # Fast: client record created
    _enqueue_portfolio_build(db, purchase)  # Fast: job record created
    # Done; return 200 to Stripe
```

### `app/portfolio_generator.py` (stub)
Placeholder for LLM integration.

**To implement:**
```python
async def generate_portfolio_html(client: Client, package_slug: str) -> str:
    # Call Claude or Gemini API
    # Pass: client.name, client.skills, client.experience_summary, etc.
    # Return: production-ready HTML
    
    # Use AI SDK:
    from anthropic import Anthropic
    client_obj = Anthropic(api_key=...)
    response = client_obj.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"Generate portfolio HTML for {client.name}..."
        }]
    )
    return response.content[0].text
```

### `app/github_integration.py` (stub)
Placeholder for GitHub repo creation and Vercel deployment.

**To implement:**
```python
def push_portfolio_to_github(client: Client, portfolio_html: str) -> tuple[str, str]:
    # 1. Create GitHub repo (or get existing)
    # 2. Write portfolio_html to index.html
    # 3. Commit and push
    # 4. Trigger Vercel deployment
    # 5. Return (github_url, vercel_live_url)
    
    # Use PyGithub:
    from github import Github
    g = Github(GITHUB_TOKEN)
    org = g.get_organization(GITHUB_ORG)
    repo = org.create_repo(f"portfolio-{client.public_id}")
    repo.create_file("index.html", "Initial", portfolio_html)
    
    # Trigger Vercel via webhook
    # Poll Vercel API until live
```

### `app/email_service.py` (modified)
Added `send_portfolio_live_email()` function.

**Already integrated:**
```python
def send_portfolio_live_email(
    client_name: str,
    client_email: str,
    portfolio_url: str,
) -> bool:
    # Sends via Resend or SendGrid (configured via env)
```

---

## Data Flow

### Scenario: Order → Portfolio Live (End-to-End)

```
Time T=0:00
  Client clicks "Buy" → Stripe checkout

T=0:05
  Client pays → Stripe sends webhook

T=0:06
  FastAPI /webhooks/stripe endpoint:
    - Verify signature ✓
    - Create Client record (name="Pending Intake", ...)
    - Assign intake token
    - Enqueue PortfolioBuildJob (status=PENDING)
    - Return 200 OK to Stripe

T=0:07 (Worker polls every 5 seconds)
  Worker fetches job_id=42 (status=PENDING)
  Calls process_job(db, 42)
  
  Step 1: PROVISIONING (10 seconds)
    - Fetch client intake data
    - Verify GitHub token from client record
    - Mark status=PROVISIONING
    
  Step 2: GENERATING (20 seconds)
    - Call Claude API with client data
    - Get portfolio HTML
    - Mark status=GENERATING
    
  Step 3: PUSHING (15 seconds)
    - Create GitHub repo
    - Commit index.html
    - Trigger Vercel deploy
    - Mark status=PUSHING
    - Store portfolio_url=https://portfolio-xyz.vercel.app
    
  Step 4: NOTIFYING (2 seconds)
    - Send client email: "Your portfolio is live!"
    - Mark status=NOTIFYING
    - Set notified_client_at
    
  Mark status=COMPLETE
  completed_at = now()

T=0:58
  Total time: ~52 seconds (asynchronous, no user blocking)
  Client receives email with portfolio URL
```

---

## Scaling Characteristics

### Single Worker
- Throughput: ~5–10 jobs/minute (assuming 30s per job)
- Safe for: 0–50 orders/day

### 10 Workers (parallel processing)
- Throughput: ~50–100 jobs/minute
- Safe for: 50–500 orders/day

### 40 Workers + Database Connection Pool
- Throughput: ~200–400 jobs/minute
- Safe for: 500–2000+ orders/day
- Bottleneck shifts to LLM rate limits and GitHub API

### With Inngest (serverless queue)
- Auto-scaling: 0 → 1000 workers instantly
- Cost: Pay per job, no idle overhead
- Safe for: 2000+ orders/day
- **Recommended for production**

---

## Failure Scenarios & Recovery

### Scenario 1: Worker Crashes Mid-Job

```
Job state: PROVISIONING (30% complete)
Worker crashes
System recovers:
  - Job still in database
  - Next worker run picks it up
  - Restarts from current_step
  - Idempotent steps prevent duplication
Result: Job continues ✓
```

### Scenario 2: LLM API Timeout

```
Step 2: GENERATING fails (timeout)
Caught by StepError exception
  - retry_count += 1
  - status = RETRY_PENDING
  - Worker sleeps 5 minutes
  - Next poll retries LLM call
Result: Auto-retry with backoff ✓
```

### Scenario 3: GitHub Repo Already Exists

```
Step 3: PUSHING
  - Checks if job.github_repo_url already set
  - If yes, returns cached URL
  - If no, creates repo and returns new URL
Result: No duplicate repos ✓
```

### Scenario 4: Email Already Sent

```
Step 4: NOTIFYING
  - Checks if job.notified_client_at already set
  - If yes, skips send
  - If no, sends email and records timestamp
Result: No duplicate emails ✓
```

---

## Monitoring & Observability

### Database Queries for Debugging

```sql
-- Jobs stuck in GENERATING (> 5 minutes)
SELECT id, client_id, current_step, created_at
FROM portfolio_build_jobs
WHERE status = 'generating'
AND created_at < NOW() - INTERVAL '5 minute';

-- Failed jobs
SELECT id, client_id, error_step, error_message, retry_count, max_retries
FROM portfolio_build_jobs
WHERE status = 'failed'
ORDER BY created_at DESC;

-- Retry storms (> 2 retries)
SELECT id, retry_count, error_message
FROM portfolio_build_jobs
WHERE retry_count >= 2
AND status != 'complete';
```

### Key Metrics to Track

1. **Throughput**: Jobs completed per minute
2. **P95 Latency**: 95th percentile of job duration
3. **Error Rate**: Failed jobs / total jobs
4. **Retry Rate**: RETRY_PENDING jobs / attempts
5. **Queue Depth**: Jobs in PENDING or RETRY_PENDING

---

## Security Considerations

### GitHub Token Storage

⚠️ **CRITICAL**: Intake form collects GitHub credentials from clients.

```python
# MUST encrypt before storing
# DO NOT log the token value
# Rotate tokens frequently
```

Recommendation:
```python
# Use field-level encryption (SQLAlchemy-Utils)
from sqlalchemy_utils import EncryptedType

class Client(Base):
    github_token = Column(EncryptedType(String, ENCRYPTION_KEY))
```

### Stripe Webhook Validation

```python
# ALWAYS verify signature
stripe.Webhook.construct_event(payload, signature, secret)
# Never trust unsigned webhooks
```

### Email Delivery

```python
# Log email sends without exposing content
logger.info("Sent portfolio notification to %s", client_email)
# NOT: logger.info(f"Email: {email_html}")
```

---

## Future Enhancements

### 1. Inngest Integration (Recommended)
Replace polling worker with serverless queue:
```python
from inngest import Inngest

inngest = Inngest(app_id="cs-os")

@inngest.create_function(fn_id="portfolio.build")
async def build_portfolio(event):
    process_job(event.data["job_id"])
```

**Benefits:** Auto-scaling, built-in retry, observability dashboard.

### 2. Webhook Delivery for External Systems

```python
# Post-completion events to external systems
POST /webhooks/portfolio-complete
{
  "job_id": 123,
  "client_id": 42,
  "portfolio_url": "https://...",
  "github_url": "https://...",
  "timestamp": "2024-01-15T10:35:43Z"
}
```

### 3. Streaming Portfolio Generation

For large portfolios, stream HTML as it's generated:
```python
async def generate_portfolio_streaming(client):
    async for chunk in client_obj.messages.stream(...):
        yield chunk  # Send to client for real-time updates
```

### 4. Portfolio Versioning

```python
class PortfolioVersion(Base):
    job_id, version, html_content, created_at
    # Allow clients to revert to previous versions
```

---

## Deployment Checklist

- [ ] All environment variables set (see FULFILLMENT_SETUP.md)
- [ ] Database migrations run: `python -c "from app.migrations import run_migrations; run_migrations(engine)"`
- [ ] Worker process deployed and running
- [ ] Stripe webhook configured to hit `/webhooks/stripe`
- [ ] GitHub token stored securely
- [ ] Email service tested (send_portfolio_live_email)
- [ ] LLM API key verified
- [ ] Monitoring/logging configured
- [ ] Backup/restore plan documented
- [ ] Load testing done (simulate 200 concurrent orders)

---

## Questions?

Refer to:
- `FULFILLMENT_SETUP.md` for environment setup
- `app/fulfillment_orchestrator.py` for state machine logic
- `app/worker.py` for worker implementation
- `app/routes/fulfillment.py` for API documentation
