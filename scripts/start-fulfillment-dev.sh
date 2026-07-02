#!/bin/bash
# Quick startup for autonomous fulfillment system in development

set -e

echo "🚀 Starting cs-os Autonomous Fulfillment System"
echo ""

# Check environment
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env.template << 'EOF'
# Database
DATABASE_URL=sqlite:///./cs_os.db

# Stripe
STRIPE_SECRET_KEY=sk_test_YOUR_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET
STRIPE_PRICE_FOUNDATION=price_foundation
STRIPE_PRICE_LAUNCH=price_launch
STRIPE_PRICE_ACCELERATOR=price_accelerator

# GitHub (for portfolio repos)
GITHUB_TOKEN=ghp_YOUR_TOKEN
GITHUB_ORG=your-org

# LLM
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY
# OR: GOOGLE_API_KEY=AIza...

# Email
EMAIL_PROVIDER=resend
RESEND_API_KEY=re_YOUR_KEY
EMAIL_FROM=noreply@yourdomain.com

# App
BASE_URL=http://localhost:8000
OPS_PASSWORD=dev-password
INTAKE_TOKEN_PEPPER=dev-pepper
EOF
    echo "✓ Template created at .env.template"
    echo "  Copy and edit: cp .env.template .env"
    exit 1
fi

echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

echo "🗄️  Initializing database..."
python -c "from app.database import engine; from app.migrations import run_migrations; run_migrations(engine)"

echo ""
echo "✅ Setup complete. Starting services..."
echo ""
echo "📡 FastAPI server: http://localhost:8000"
echo "📊 Worker: Processing jobs from queue"
echo ""

# Start server and worker in parallel
(
    echo "Starting FastAPI server..."
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
) &
SERVER_PID=$!

(
    # Give server a moment to start
    sleep 2
    echo "Starting background worker..."
    python -m app.worker --poll-interval 5 --batch-size 10
) &
WORKER_PID=$!

# Handle shutdown
trap "kill $SERVER_PID $WORKER_PID 2>/dev/null; exit 0" SIGINT SIGTERM

echo ""
echo "🎯 Ready! Server PID=$SERVER_PID, Worker PID=$WORKER_PID"
echo ""
echo "Test webhook:"
echo '  curl -X POST http://localhost:8000/webhooks/stripe \\'
echo '    -H "Stripe-Signature: t=123,v1=abc" \\'
echo '    -d @test-webhook.json'
echo ""
echo "Check job status:"
echo "  curl http://localhost:8000/builds/status?client_id=1"
echo ""

# Wait for both processes
wait
