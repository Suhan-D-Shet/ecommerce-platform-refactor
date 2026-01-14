#!/bin/bash

# Install systemd service for E-Commerce API

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Installing E-Commerce API systemd service...${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    exit 1
fi

# Get the project directory
PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR"
PROJECT_DIR=$(pwd)

echo -e "${BLUE}Project directory: $PROJECT_DIR${NC}"

# Create ecommerce user if it doesn't exist
if id "ecommerce" &>/dev/null; then
    echo -e "${YELLOW}User 'ecommerce' already exists${NC}"
else
    echo -e "${BLUE}Creating 'ecommerce' user...${NC}"
    useradd -r -s /bin/bash -d "$PROJECT_DIR" -m ecommerce
    echo -e "${GREEN}User 'ecommerce' created${NC}"
fi

# Create log directory
LOG_DIR="/var/log/ecommerce-api"
mkdir -p "$LOG_DIR"
chown ecommerce:ecommerce "$LOG_DIR"
chmod 755 "$LOG_DIR"
echo -e "${GREEN}Log directory created: $LOG_DIR${NC}"

# Copy service file
echo -e "${BLUE}Installing systemd service file...${NC}"
cp ecommerce-api.service /etc/systemd/system/
chmod 644 /etc/systemd/system/ecommerce-api.service
echo -e "${GREEN}Service file installed${NC}"

# Update WorkingDirectory in service file
sed -i "s|WorkingDirectory=/opt/ecommerce-api|WorkingDirectory=$PROJECT_DIR|g" /etc/systemd/system/ecommerce-api.service
sed -i "s|Environment=\"PATH=/opt/ecommerce-api/venv/bin\"|Environment=\"PATH=$PROJECT_DIR/venv/bin\"|g" /etc/systemd/system/ecommerce-api.service
sed -i "s|EnvironmentFile=/opt/ecommerce-api/.env|EnvironmentFile=$PROJECT_DIR/.env|g" /etc/systemd/system/ecommerce-api.service
sed -i "s|ExecStart=/opt/ecommerce-api/venv/bin/gunicorn|ExecStart=$PROJECT_DIR/venv/bin/gunicorn|g" /etc/systemd/system/ecommerce-api.service

# Reload systemd daemon
systemctl daemon-reload
echo -e "${GREEN}systemd daemon reloaded${NC}"

# Set proper permissions
chown -R ecommerce:ecommerce "$PROJECT_DIR"
chmod -R 750 "$PROJECT_DIR"
chmod 640 "$PROJECT_DIR/.env"

# Display instructions
echo ""
echo -e "${GREEN}=================================================="
echo "Service installation completed!"
echo "==================================================${NC}"
echo ""
echo "To manage the service, use:"
echo "  sudo systemctl start ecommerce-api       # Start the service"
echo "  sudo systemctl stop ecommerce-api        # Stop the service"
echo "  sudo systemctl restart ecommerce-api     # Restart the service"
echo "  sudo systemctl status ecommerce-api      # Check status"
echo "  sudo systemctl enable ecommerce-api      # Enable at boot"
echo "  sudo systemctl disable ecommerce-api     # Disable at boot"
echo ""
echo "View logs with:"
echo "  sudo journalctl -u ecommerce-api -f      # Live logs"
echo "  sudo journalctl -u ecommerce-api --tail 50 # Last 50 lines"
echo ""
echo "Install gunicorn first if not already installed:"
echo "  source $PROJECT_DIR/venv/bin/activate"
echo "  pip install gunicorn"
echo ""
