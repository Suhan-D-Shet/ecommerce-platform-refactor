# E-Commerce Platform - Linux Deployment Guide

This guide provides step-by-step instructions for deploying the FastAPI e-commerce backend on Linux systems (Ubuntu 20.04+ or Debian 11+).

## Table of Contents

1. [Quick Start](#quick-start)
2. [Manual Installation](#manual-installation)
3. [Automated Setup](#automated-setup)
4. [Database Management](#database-management)
5. [Running as a Service](#running-as-a-service)
6. [Production Deployment](#production-deployment)
7. [Backup and Recovery](#backup-and-recovery)
8. [Monitoring and Logs](#monitoring-and-logs)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

- Ubuntu 20.04 LTS or Debian 11+ system
- sudo access
- At least 2GB RAM and 10GB disk space

### One-Command Setup

```bash
wget https://your-repo-url/setup.sh -O setup.sh
chmod +x setup.sh
./setup.sh
```

This will automatically:
- Install Python 3, PostgreSQL, and dependencies
- Create Python virtual environment
- Install Python packages
- Setup database and user
- Create necessary directories
- Prompt to seed sample data

Then start the server:

```bash
source venv/bin/activate
python main.py
```

Access the API at: `http://localhost:8000`
View docs at: `http://localhost:8000/docs`

---

## Manual Installation

### Step 1: Install System Dependencies

```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    postgresql \
    postgresql-contrib \
    git \
    curl \
    wget
```

### Step 2: Clone/Download Project

```bash
cd /opt
sudo git clone https://your-repo-url ecommerce-api
cd ecommerce-api
sudo chown -R $USER:$USER .
```

### Step 3: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
```

### Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure Database

#### Start PostgreSQL

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Create Database and User

```bash
sudo -u postgres psql << EOF
CREATE USER ecommerce_user WITH PASSWORD 'ecommerce_password';
ALTER ROLE ecommerce_user SET client_encoding TO 'utf8';
ALTER ROLE ecommerce_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ecommerce_user SET default_transaction_deferrable TO on;
ALTER ROLE ecommerce_user SET default_transaction_read_uncommitted TO off;
CREATE DATABASE ecommerce_db OWNER ecommerce_user;
GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO ecommerce_user;
EOF
```

### Step 6: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and configure:

```bash
nano .env
```

Required variables:

```env
DATABASE_URL=postgresql://ecommerce_user:ecommerce_password@localhost:5432/ecommerce_db
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Generate a secure SECRET_KEY:**

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 7: Initialize Database

```bash
python scripts/seed_data.py
```

### Step 8: Test the Application

```bash
python main.py
```

Should output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## Automated Setup

For complete automation, use the provided setup script:

```bash
chmod +x setup.sh
./setup.sh
```

This handles all steps above automatically and creates necessary directories.

---

## Database Management

### Create a Backup

```bash
bash scripts/backup-database.sh
```

Backup files are stored in the `backups/` directory with timestamp format:
`ecommerce_backup_YYYYMMDD_HHMMSS.sql.gz`

### Restore from Backup

```bash
bash scripts/restore-database.sh backups/ecommerce_backup_20240115_140530.sql.gz
```

### Automatic Daily Backups

Add to crontab (run `crontab -e`):

```bash
0 2 * * * cd /opt/ecommerce-api && source venv/bin/activate && bash scripts/auto-backup.sh
```

This backs up the database daily at 2 AM.

### Backup Management UI

```bash
bash scripts/backup-restore-manager.sh
```

Interactive menu for backup operations.

---

## Running as a Service

### Install Gunicorn

```bash
source venv/bin/activate
pip install gunicorn
```

### Install SystemD Service

```bash
sudo bash scripts/install-service.sh /opt/ecommerce-api
```

### Manage Service

```bash
# Start service
sudo systemctl start ecommerce-api

# Stop service
sudo systemctl stop ecommerce-api

# Restart service
sudo systemctl restart ecommerce-api

# Enable at boot
sudo systemctl enable ecommerce-api

# Check status
sudo systemctl status ecommerce-api

# View logs
sudo journalctl -u ecommerce-api -f
```

---

## Production Deployment

### 1. Configure Environment

Set `ENVIRONMENT=production` in `.env` and use a strong `SECRET_KEY`.

### 2. Setup Nginx Reverse Proxy

Create `/etc/nginx/sites-available/ecommerce-api`:

```nginx
upstream ecommerce_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    client_max_body_size 100M;

    location / {
        proxy_pass http://ecommerce_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/ecommerce-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. SSL Certificate (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d your-domain.com
```

### 4. Firewall Configuration

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 5. Performance Tuning

Edit `/etc/systemd/system/ecommerce-api.service` to increase workers:

```ini
ExecStart=/opt/ecommerce-api/venv/bin/gunicorn \
    --workers 8 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    main:app
```

Reload:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ecommerce-api
```

---

## Backup and Recovery

### Backup Locations

- Database backups: `./backups/`
- Application logs: `./logs/`
- Configuration: `./.env`

### Backup Strategy

1. **Daily database backups** (via cron)
2. **Weekly full system backups** (OS level)
3. **Keep last 10 database backups** (automatic cleanup)

### Full System Backup

```bash
sudo tar -czf /backup/ecommerce-api-$(date +%Y%m%d).tar.gz \
    /opt/ecommerce-api \
    /etc/nginx/sites-available/ecommerce-api \
    /etc/systemd/system/ecommerce-api.service
```

---

## Monitoring and Logs

### View Live Logs

```bash
# Service logs
sudo journalctl -u ecommerce-api -f

# Access logs
tail -f logs/access.log

# Error logs
tail -f logs/error.log
```

### Monitor Service Status

```bash
# Check if service is running
sudo systemctl status ecommerce-api

# Check system resources
top
htop  # requires: sudo apt-get install htop

# Check database connections
sudo -u postgres psql ecommerce_db -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"
```

### Log Rotation

Create `/etc/logrotate.d/ecommerce-api`:

```
/opt/ecommerce-api/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ecommerce ecommerce
}
```

---

## Troubleshooting

### Service Won't Start

Check logs:
```bash
sudo journalctl -u ecommerce-api -n 50
```

Common issues:
- Port 8000 already in use: `lsof -i :8000`
- Database connection error: Verify DATABASE_URL in .env
- Missing dependencies: Run `pip install -r requirements.txt`

### Database Connection Issues

Test connection:
```bash
psql postgresql://ecommerce_user:ecommerce_password@localhost:5432/ecommerce_db
```

### High Memory Usage

Reduce worker count in service file:
```bash
--workers 2
```

### API Endpoints Not Responding

1. Check if service is running: `systemctl status ecommerce-api`
2. Check nginx proxy: `sudo nginx -t`
3. Check firewall: `sudo ufw status`
4. Check if port is open: `curl http://localhost:8000/docs`

### Backup Restore Failed

1. Ensure PostgreSQL is running: `sudo systemctl status postgresql`
2. Check disk space: `df -h`
3. Verify backup file exists and is valid: `file backups/ecommerce_backup_*.sql.gz`

---

## Security Checklist

- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Change database password from default
- [ ] Enable firewall and allow only needed ports
- [ ] Setup SSL certificate (Let's Encrypt)
- [ ] Disable unnecessary services
- [ ] Keep system packages updated: `sudo apt-get update && sudo apt-get upgrade`
- [ ] Setup automated backups
- [ ] Monitor logs regularly
- [ ] Restrict file permissions on `.env` file

---

## Support

For issues or questions, refer to:
- API Documentation: `http://your-domain.com/docs`
- Application logs: `./logs/`
- Backup logs: `./backups/backup.log`
