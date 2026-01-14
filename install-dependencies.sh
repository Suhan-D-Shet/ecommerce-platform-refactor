#!/bin/bash

# Install system dependencies for Linux

set -e

echo "Installing system dependencies..."

# Update package manager
sudo apt-get update

# Install Python and related tools
echo "Installing Python..."
sudo apt-get install -y python3 python3-pip python3-venv python3-dev

# Install PostgreSQL
echo "Installing PostgreSQL..."
sudo apt-get install -y postgresql postgresql-contrib postgresql-client

# Install additional tools for development
echo "Installing development tools..."
sudo apt-get install -y build-essential libpq-dev git curl wget

# Install supervisor for process management (optional)
echo "Installing supervisor..."
sudo apt-get install -y supervisor

# Install nginx for reverse proxy (optional)
echo "Installing nginx..."
sudo apt-get install -y nginx

echo "System dependencies installed successfully!"
