# E-Commerce API - Quick Reference Guide

## Starting & Stopping

```bash
# Development mode
source venv/bin/activate
python main.py

# Production mode (as service)
sudo systemctl start ecommerce-api
sudo systemctl stop ecommerce-api
sudo systemctl restart ecommerce-api
```

## Database Operations

```bash
# Create backup
bash scripts/backup-database.sh

# Restore from backup
bash scripts/restore-database.sh backups/ecommerce_backup_YYYYMMDD_HHMMSS.sql.gz

# Access database directly
psql postgresql://ecommerce_user:ecommerce_password@localhost:5432/ecommerce_db

# Check database size
sudo -u postgres psql ecommerce_db -c "SELECT pg_size_pretty(pg_database_size('ecommerce_db'));"
```

## Logs

```bash
# Service logs (live)
sudo journalctl -u ecommerce-api -f

# Last 50 lines
sudo journalctl -u ecommerce-api --tail 50

# Application logs
tail -f logs/access.log
tail -f logs/error.log

# Backup logs
tail -f backups/backup.log
```

## API Endpoints

```
GET  /docs                          # Swagger UI
GET  /redoc                         # ReDoc documentation
GET  /openapi.json                  # OpenAPI schema

# Authentication
POST /auth/register                 # Register new user
POST /auth/login                    # Login user

# Categories
GET  /categories                    # List categories
POST /categories                    # Create category
GET  /categories/{id}              # Get category
PUT  /categories/{id}              # Update category
DELETE /categories/{id}            # Delete category

# Products
GET  /products                      # List products (with filters & pagination)
POST /products                      # Create product
GET  /products/{id}                # Get product
PUT  /products/{id}                # Update product
DELETE /products/{id}              # Delete product

# Shopping Cart
GET  /cart                          # Get cart
POST /cart/items                    # Add to cart
PUT  /cart/items/{item_id}         # Update cart item
DELETE /cart/items/{item_id}       # Remove from cart
DELETE /cart                        # Clear cart

# Orders
POST /orders/checkout               # Create order from cart
GET  /orders                        # Get order history
GET  /orders/{id}                  # Get order details

# Reviews
POST /products/{id}/reviews         # Add review
GET  /products/{id}/reviews         # Get product reviews

# Coupons
GET  /coupons/{code}               # Validate coupon

# Shipping
POST /shipping/calculate            # Calculate shipping cost
```

## Environment Variables

```bash
# .env file must contain:
DATABASE_URL=postgresql://user:password@localhost:5432/db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## Performance Monitoring

```bash
# Check service status
systemctl status ecommerce-api

# View process info
ps aux | grep ecommerce

# Monitor system resources
top
htop

# Check port 8000 usage
lsof -i :8000

# Database connections
sudo -u postgres psql ecommerce_db -c "SELECT count(*) FROM pg_stat_activity;"

# API response time (requires curl)
curl -w "Total: %{time_total}s\n" -o /dev/null -s http://localhost:8000/
```

## Troubleshooting Commands

```bash
# Test database connection
psql postgresql://ecommerce_user:ecommerce_password@localhost:5432/ecommerce_db -c "\dt"

# Test API connectivity
curl http://localhost:8000/docs

# Check if port is in use
netstat -tulpn | grep 8000

# View service error
systemctl status ecommerce-api -n 20

# Reload systemd
sudo systemctl daemon-reload

# Check nginx config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Check firewall rules
sudo ufw status verbose

# View last 100 backup operations
tail -100 backups/backup.log
```

## Common Tasks

### Update Dependencies
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
sudo systemctl restart ecommerce-api
```

### Change Secret Key
```bash
# Generate new key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env
nano .env

# Restart service
sudo systemctl restart ecommerce-api
```

### Schedule Daily Backup
```bash
crontab -e
# Add: 0 2 * * * cd /opt/ecommerce-api && source venv/bin/activate && bash scripts/auto-backup.sh
```

### View Database Stats
```bash
sudo -u postgres psql ecommerce_db << EOF
\dt+
SELECT * FROM pg_stat_user_tables;
EOF
```

### Clean Old Logs
```bash
find logs/ -name "*.log" -mtime +30 -delete
find backups/ -name "*.sql.gz" -mtime +60 -delete
```

---

**For detailed information, refer to LINUX_DEPLOYMENT.md**
