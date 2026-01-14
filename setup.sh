#!/bin/bash

# E-Commerce Platform - Linux Setup Script
# This script automates the setup of the FastAPI backend on Linux systems

set -e  # Exit on any error

echo "=================================================="
echo "E-Commerce FastAPI Backend - Linux Setup"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python 3.9+ is installed
echo -e "${BLUE}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python3 not found. Installing...${NC}"
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
else
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}Python ${PYTHON_VERSION} found${NC}"
fi

# Check if PostgreSQL is installed
echo -e "${BLUE}Checking PostgreSQL...${NC}"
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}PostgreSQL not found. Installing...${NC}"
    sudo apt-get update
    sudo apt-get install -y postgresql postgresql-contrib
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    echo -e "${GREEN}PostgreSQL installed and started${NC}"
else
    echo -e "${GREEN}PostgreSQL found${NC}"
fi

# Create project directory if it doesn't exist
PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR"

# Create virtual environment
echo -e "${BLUE}Creating Python virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Skipping creation.${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel

# Install dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}Dependencies installed${NC}"
else
    echo -e "${YELLOW}requirements.txt not found${NC}"
fi

# Create .env file if it doesn't exist
echo -e "${BLUE}Setting up environment variables...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || {
        cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://ecommerce_user:ecommerce_password@localhost:5432/ecommerce_db

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
EOF
    }
    echo -e "${GREEN}.env file created. Please update it with your configuration.${NC}"
else
    echo -e "${GREEN}.env file already exists${NC}"
fi

# Create PostgreSQL database and user
echo -e "${BLUE}Setting up PostgreSQL database...${NC}"
sudo -u postgres psql << EOF
SELECT 1 FROM pg_database WHERE datname = 'ecommerce_db' LIMIT 1;
EOF

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Creating PostgreSQL database and user...${NC}"
    sudo -u postgres psql << EOF
CREATE USER ecommerce_user WITH PASSWORD 'ecommerce_password';
ALTER ROLE ecommerce_user SET client_encoding TO 'utf8';
ALTER ROLE ecommerce_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ecommerce_user SET default_transaction_deferrable TO on;
ALTER ROLE ecommerce_user SET default_transaction_read_uncommitted TO off;
CREATE DATABASE ecommerce_db OWNER ecommerce_user;
GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO ecommerce_user;
EOF
    echo -e "${GREEN}PostgreSQL database and user created${NC}"
else
    echo -e "${GREEN}PostgreSQL database already exists${NC}"
fi

# Create backup directory
echo -e "${BLUE}Creating backup directory...${NC}"
mkdir -p backups
chmod 755 backups
echo -e "${GREEN}Backup directory created${NC}"

# Create logs directory
echo -e "${BLUE}Creating logs directory...${NC}"
mkdir -p logs
chmod 755 logs
echo -e "${GREEN}Logs directory created${NC}"

# Run seed script if it exists
echo -e "${BLUE}Checking for seed data...${NC}"
if [ -f "scripts/seed_data.py" ]; then
    read -p "Do you want to seed the database with sample data? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Seeding database...${NC}"
        python scripts/seed_data.py
        echo -e "${GREEN}Database seeded${NC}"
    fi
fi

# Display final instructions
echo ""
echo -e "${GREEN}=================================================="
echo "Setup completed successfully!"
echo "==================================================${NC}"
echo ""
echo "Next steps:"
echo "1. Update .env file with your configuration"
echo "2. Change the SECRET_KEY in .env to a secure random value"
echo "3. Run the application: python main.py"
echo "4. Access the API at http://localhost:8000"
echo "5. View API documentation at http://localhost:8000/docs"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
