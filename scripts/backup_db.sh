#!/bin/bash
# Database backup script for VoteWise2
# Backs up PostgreSQL database and keeps last 7 days of backups

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ .env file not found!"
    exit 1
fi

# Configuration
BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/votewise_backup_$TIMESTAMP.sql"
RETENTION_DAYS=7

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

echo "🗄️  Starting database backup..."
echo "Database: $DB_NAME"
echo "Backup file: ${BACKUP_FILE}.gz"

# Perform backup
PGPASSWORD=$DB_PASSWORD pg_dump \
    -h $DB_HOST \
    -p ${DB_PORT:-5432} \
    -U $DB_USER \
    -d $DB_NAME \
    --no-owner \
    --no-acl \
    > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Calculate backup size
BACKUP_SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)

echo "✅ Database backed up successfully!"
echo "File: ${BACKUP_FILE}.gz"
echo "Size: $BACKUP_SIZE"

# Clean up old backups
echo "🧹 Cleaning up old backups (keeping last $RETENTION_DAYS days)..."
find $BACKUP_DIR -name "votewise_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# List remaining backups
BACKUP_COUNT=$(find $BACKUP_DIR -name "votewise_backup_*.sql.gz" | wc -l)
echo "📦 Total backups: $BACKUP_COUNT"

echo "✅ Backup complete!"
