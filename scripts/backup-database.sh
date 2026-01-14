#!/bin/bash

# PostgreSQL Database Backup Script
# Creates a backup of the ecommerce database with timestamp

set -e

# Configuration
DB_NAME="ecommerce_db"
DB_USER="ecommerce_user"
BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/ecommerce_backup_${TIMESTAMP}.sql"
LOG_FILE="${BACKUP_DIR}/backup.log"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "${BLUE}Starting database backup...${NC}"

# Check if PostgreSQL is running
if ! sudo systemctl is-active --quiet postgresql; then
    log "${RED}Error: PostgreSQL is not running${NC}"
    exit 1
fi

# Create backup
if pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "${GREEN}Backup successful!${NC}"
    log "Backup file: $BACKUP_FILE"
    log "Backup size: $BACKUP_SIZE"
else
    log "${RED}Error: Backup failed${NC}"
    exit 1
fi

# Compress the backup
log "${BLUE}Compressing backup...${NC}"
gzip "$BACKUP_FILE"
COMPRESSED_FILE="${BACKUP_FILE}.gz"
COMPRESSED_SIZE=$(du -h "$COMPRESSED_FILE" | cut -f1)
log "${GREEN}Backup compressed to: $COMPRESSED_FILE${NC}"
log "Compressed size: $COMPRESSED_SIZE"

# Keep only the last 10 backups
log "${BLUE}Cleaning up old backups (keeping last 10)...${NC}"
ls -1t "${BACKUP_DIR}"/ecommerce_backup_*.sql.gz 2>/dev/null | tail -n +11 | xargs -r rm -f

log "${GREEN}Backup process completed${NC}"
