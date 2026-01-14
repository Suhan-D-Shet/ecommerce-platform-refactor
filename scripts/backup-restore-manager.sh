#!/bin/bash

# Backup and Restore Management Utility
# Provides an interactive menu for backup operations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_DIR}/backups"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

clear
echo -e "${BLUE}=================================================="
echo "E-Commerce Database Backup Manager"
echo "==================================================${NC}"
echo ""

while true; do
    echo "Options:"
    echo "1. Create a new backup"
    echo "2. Restore from backup"
    echo "3. List all backups"
    echo "4. Delete old backups"
    echo "5. Schedule automatic backups"
    echo "6. Exit"
    echo ""
    read -p "Select an option (1-6): " choice

    case $choice in
        1)
            echo ""
            echo -e "${BLUE}Creating backup...${NC}"
            bash "${SCRIPT_DIR}/backup-database.sh"
            echo ""
            ;;
        2)
            echo ""
            echo -e "${BLUE}Available backups:${NC}"
            if ls -1 "${BACKUP_DIR}"/ecommerce_backup_*.sql.gz 2>/dev/null | nl; then
                read -p "Enter backup filename to restore: " backup_file
                if [ -f "${BACKUP_DIR}/$backup_file" ]; then
                    bash "${SCRIPT_DIR}/restore-database.sh" "${BACKUP_DIR}/$backup_file"
                else
                    echo -e "${RED}Error: Backup file not found${NC}"
                fi
            else
                echo -e "${YELLOW}No backups found${NC}"
            fi
            echo ""
            ;;
        3)
            echo ""
            echo -e "${BLUE}Backup files:${NC}"
            if ls -lh "${BACKUP_DIR}"/ecommerce_backup_*.sql.gz 2>/dev/null; then
                echo ""
                echo "Total backups:"
                ls -1 "${BACKUP_DIR}"/ecommerce_backup_*.sql.gz 2>/dev/null | wc -l
            else
                echo -e "${YELLOW}No backups found${NC}"
            fi
            echo ""
            ;;
        4)
            echo ""
            echo -e "${YELLOW}Deleting backups older than 30 days...${NC}"
            find "${BACKUP_DIR}" -name "ecommerce_backup_*.sql.gz" -mtime +30 -delete
            echo -e "${GREEN}Old backups deleted${NC}"
            echo ""
            ;;
        5)
            echo ""
            echo -e "${BLUE}Setting up automatic backups...${NC}"
            echo "Add this line to your crontab (crontab -e) to backup daily at 2 AM:"
            echo ""
            echo -e "${YELLOW}0 2 * * * cd ${PROJECT_DIR} && source venv/bin/activate && bash ${SCRIPT_DIR}/auto-backup.sh${NC}"
            echo ""
            ;;
        6)
            echo -e "${GREEN}Exiting...${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option. Please select 1-6.${NC}"
            echo ""
            ;;
    esac
done
