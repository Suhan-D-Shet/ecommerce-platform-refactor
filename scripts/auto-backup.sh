#!/bin/bash

# Automated Backup Cron Script
# Schedule this with crontab for automatic backups

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment
source "${PROJECT_DIR}/venv/bin/activate"

# Change to project directory
cd "$PROJECT_DIR"

# Run backup
"${SCRIPT_DIR}/backup-database.sh"

# Send summary email (optional - requires mail utility)
BACKUP_DIR="${PROJECT_DIR}/backups"
LATEST_BACKUP=$(ls -t "${BACKUP_DIR}"/ecommerce_backup_*.sql.gz 2>/dev/null | head -1)

if [ ! -z "$LATEST_BACKUP" ]; then
    BACKUP_SIZE=$(du -h "$LATEST_BACKUP" | cut -f1)
    BACKUP_DATE=$(date +"%Y-%m-%d %H:%M:%S")
    
    # Log the backup info
    echo "Backup completed at $BACKUP_DATE - Size: $BACKUP_SIZE" >> "${BACKUP_DIR}/backup.log"
fi
