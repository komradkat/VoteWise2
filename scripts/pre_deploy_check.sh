#!/bin/bash
# Pre-deployment validation script
# Run this before deploying to production

set -e

echo "🔍 Running pre-deployment checks for VoteWise2..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}❌ .env file not found!${NC}"
    exit 1
fi

# Check required environment variables
echo "📋 Checking required environment variables..."
required_vars=("SECRET_KEY" "DB_NAME" "DB_USER" "DB_PASSWORD" "ALLOWED_HOSTS")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Missing required environment variable: $var${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✓${NC} $var is set"
    fi
done

# Check DEBUG is False
if [ "$DEBUG" == "True" ]; then
    echo -e "${RED}❌ DEBUG is set to True! Must be False in production${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} DEBUG is False"
fi

# Check database connection
echo ""
echo "🗄️  Checking database connection..."
python manage.py check --database default --settings=project_config.settings.production 2>&1 | grep -q "System check identified no issues" && {
    echo -e "${GREEN}✓${NC} Database connection successful"
} || {
    echo -e "${RED}❌ Database connection failed${NC}"
    ERRORS=$((ERRORS + 1))
}

# Check for pending migrations
echo ""
echo "🔄 Checking for pending migrations..."
PENDING=$(python manage.py showmigrations --settings=project_config.settings.production | grep '\[ \]' | wc -l)
if [ $PENDING -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Warning: $PENDING pending migration(s) found${NC}"
    python manage.py showmigrations --settings=project_config.settings.production | grep '\[ \]'
else
    echo -e "${GREEN}✓${NC} No pending migrations"
fi

# Run Django deployment checks
echo ""
echo "🔐 Running Django deployment checks..."
python manage.py check --deploy --settings=project_config.settings.production 2>&1 | tee /tmp/django_check.log

if grep -q "System check identified no issues" /tmp/django_check.log; then
    echo -e "${GREEN}✓${NC} Django deployment checks passed"
else
    echo -e "${YELLOW}⚠️  Django deployment checks found issues (review above)${NC}"
fi

# Check static files directory
echo ""
echo "📁 Checking static files..."
if [ -d "staticfiles" ]; then
    FILE_COUNT=$(find staticfiles -type f | wc -l)
    if [ $FILE_COUNT -gt 0 ]; then
        echo -e "${GREEN}✓${NC} Static files collected ($FILE_COUNT files)"
    else
        echo -e "${YELLOW}⚠️  Static files directory is empty. Run: python manage.py collectstatic${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Static files directory not found. Run: python manage.py collectstatic${NC}"
fi

# Check logs directory
echo ""
echo "📝 Checking logs directory..."
if [ -d "logs" ]; then
    echo -e "${GREEN}✓${NC} Logs directory exists"
else
    echo -e "${YELLOW}⚠️  Creating logs directory...${NC}"
    mkdir -p logs
fi

# Summary
echo ""
echo "================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All pre-deployment checks passed!${NC}"
    echo "Ready to deploy to production."
    exit 0
else
    echo -e "${RED}❌ Pre-deployment checks failed with $ERRORS error(s)${NC}"
    echo "Fix the errors above before deploying."
    exit 1
fi
