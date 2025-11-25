#!/bin/bash
# VoteWise2 Production Deployment Script
# This script automates the deployment process

set -e  # Exit on error

echo "🚀 Starting VoteWise2 deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    echo "📝 Loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}❌ .env file not found!${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Create one with: python -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Pull latest code (optional, comment out if deploying from local)
if [ "$1" == "--pull" ]; then
    echo "📥 Pulling latest code from git..."
    git pull origin main
fi

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Run pre-deployment checks
echo "🔍 Running pre-deployment checks..."
python manage.py check --deploy --settings=project_config.settings.production

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs staticfiles media backups

# Run database migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --settings=project_config.settings.production --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --settings=project_config.settings.production --noinput --clear

# Restart services (requires sudo)
if command -v systemctl &> /dev/null; then
    echo "🔄 Restarting services..."
    sudo systemctl restart votewise || echo -e "${YELLOW}⚠️  Could not restart votewise service${NC}"
    sudo systemctl reload nginx || echo -e "${YELLOW}⚠️  Could not reload nginx${NC}"
else
    echo -e "${YELLOW}⚠️  systemctl not found, skipping service restart${NC}"
fi

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Verify the application is running: curl https://your-domain.com/health/"
echo "2. Check logs: tail -f logs/gunicorn_error.log"
echo "3. Monitor system: systemctl status votewise"
