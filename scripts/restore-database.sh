#!/bin/bash

# PostgreSQL Database Restore Script
# Restores the database from a backup file

set -e

# Configuration
DB_NAME="ecommerce_db"
DB_USER="ecommerce_user"
BACKUP_DIR="backups"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Log function
log() {
    echo -e "${1}"
}

# Check if backup file is provided
if [ -z "$1" ]; then
    log "${YELLOW}Usage: ./restore-database.sh <backup_file>${NC}"
    log ""
    log "Available backups:"
    ls -lh "${BACKUP_DIR}"/ecommerce_backup_*.sql.gz 2>/dev/null || log "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    log "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

# Confirm restore
log "${YELLOW}WARNING: This will overwrite the current database!${NC}"
read -p "Are you sure you want to restore from $BACKUP_FILE? (yes/no) " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    log "Restore cancelled"
    exit 1
fi

log "${BLUE}Starting database restore...${NC}"

# Check if PostgreSQL is running
if ! sudo systemctl is-active --quiet postgresql; then
    log "${RED}Error: PostgreSQL is not running${NC}"
    exit 1
fi

# Extract if backup is compressed
if [[ "$BACKUP_FILE" == *.gz ]]; then
    log "${BLUE}Extracting backup...${NC}"
    EXTRACTED_FILE="${BACKUP_FILE%.gz}"
    gunzip -c "$BACKUP_FILE" > "$EXTRACTED_FILE"
    BACKUP_FILE="$EXTRACTED_FILE"
fi

# Drop existing database
log "${BLUE}Dropping existing database...${NC}"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;" || true

# Create new database
log "${BLUE}Creating new database...${NC}"
sudo -u postgres psql << EOF
CREATE DATABASE $DB_NAME OWNER $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

# Restore from backup
log "${BLUE}Restoring from backup...${NC}"
if psql -U "$DB_USER" "$DB_NAME" < "$BACKUP_FILE"; then
    log "${GREEN}Database restored successfully!${NC}"
else
    log "${RED}Error: Restore failed${NC}"
    exit 1
fi

# Clean up extracted file
if [[ "$1" == *.gz ]]; then
    rm -f "$BACKUP_FILE"
fi

log "${GREEN}Restore process completed${NC}"
