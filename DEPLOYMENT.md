# Stock Research Platform - Deployment Guide

## Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Python 3.10+
- MySQL/MariaDB 10.5+
- Redis 6.0+
- Nginx
- Supervisor (for process management)

## Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nginx redis-server mysql-server supervisor git

# Install MySQL/MariaDB
sudo apt install mariadb-server mariadb-client
sudo mysql_secure_installation
```

## Step 2: Database Setup

```bash
# Login to MySQL
sudo mysql -u root -p

# Create database and user
CREATE DATABASE stock_research_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'stock_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON stock_research_platform.* TO 'stock_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## Step 3: Application Deployment

```bash
# Create application directory
sudo mkdir -p /var/www/stock_research_platform
cd /var/www/stock_research_platform

# Clone repository (or upload files)
git clone <your-repo-url> .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Create necessary directories
mkdir -p logs media staticfiles

# Set permissions
sudo chown -R www-data:www-data /var/www/stock_research_platform
sudo chmod -R 755 /var/www/stock_research_platform
```

## Step 4: Environment Configuration

```bash
# Copy and edit production environment file
cp .env.production.template .env
nano .env

# Generate new SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Update .env with:
# - Generated SECRET_KEY
# - Database credentials
# - Email configuration
# - Domain name
```

## Step 5: Django Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Set production settings
export DJANGO_SETTINGS_MODULE=config.settings.production

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Test configuration
python manage.py check --deploy
```

## Step 6: Gunicorn Setup with Supervisor

Create supervisor configuration:

```bash
sudo nano /etc/supervisor/conf.d/stock_research.conf
```

Add:

```ini
[program:stock_research]
command=/var/www/stock_research_platform/venv/bin/gunicorn config.wsgi:application -c gunicorn_config.py
directory=/var/www/stock_research_platform
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/www/stock_research_platform/logs/gunicorn.log
environment=DJANGO_SETTINGS_MODULE="config.settings.production"
```

Start Gunicorn:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start stock_research
sudo supervisorctl status
```

## Step 7: Celery Setup with Supervisor

Create Celery worker configuration:

```bash
sudo nano /etc/supervisor/conf.d/celery_worker.conf
```

Add:

```ini
[program:celery_worker]
command=/var/www/stock_research_platform/venv/bin/celery -A celery_app worker -l info
directory=/var/www/stock_research_platform
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/www/stock_research_platform/logs/celery_worker.log
environment=DJANGO_SETTINGS_MODULE="config.settings.production"
```

Create Celery beat configuration:

```bash
sudo nano /etc/supervisor/conf.d/celery_beat.conf
```

Add:

```ini
[program:celery_beat]
command=/var/www/stock_research_platform/venv/bin/celery -A celery_app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=/var/www/stock_research_platform
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/www/stock_research_platform/logs/celery_beat.log
environment=DJANGO_SETTINGS_MODULE="config.settings.production"
```

Start Celery:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start celery_worker
sudo supervisorctl start celery_beat
```

## Step 8: Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/stock_research
```

Add:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 5M;

    location /static/ {
        alias /var/www/stock_research_platform/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/stock_research_platform/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

Enable site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/stock_research /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 9: SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## Step 10: Configure Celery Periodic Tasks

Login to Django admin and configure periodic tasks:

1. Go to `/admin/django_celery_beat/periodictask/`
2. Add periodic tasks:
   - **Monitor Calls**: Run `apps.lifecycle.tasks.monitor_calls_task` every 15 minutes
   - **Update Broker Metrics**: Run `apps.lifecycle.tasks.update_broker_metrics_task` daily at 6 PM
   - **Send Daily Summary**: Run `apps.lifecycle.tasks.send_daily_summary_task` daily at 8 AM
   - **Cleanup Notifications**: Run `apps.lifecycle.tasks.cleanup_old_notifications_task` weekly

## Step 11: Monitoring & Maintenance

### View Logs

```bash
# Application logs
tail -f /var/www/stock_research_platform/logs/production.log

# Gunicorn logs
tail -f /var/www/stock_research_platform/logs/gunicorn.log

# Celery logs
tail -f /var/www/stock_research_platform/logs/celery_worker.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Restart Services

```bash
# Restart Gunicorn
sudo supervisorctl restart stock_research

# Restart Celery
sudo supervisorctl restart celery_worker
sudo supervisorctl restart celery_beat

# Restart Nginx
sudo systemctl restart nginx
```

### Database Backup

```bash
# Create backup script
sudo nano /usr/local/bin/backup_stock_db.sh
```

Add:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/stock_research"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
mysqldump -u stock_user -p'your_password' stock_research_platform | gzip > $BACKUP_DIR/backup_$DATE.sql.gz
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

```bash
sudo chmod +x /usr/local/bin/backup_stock_db.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup_stock_db.sh
```

## Step 12: Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong database passwords
- [ ] Enable firewall (ufw)
- [ ] Configure fail2ban
- [ ] Set up SSL/HTTPS
- [ ] Configure CORS if needed
- [ ] Enable Django security middleware
- [ ] Set up monitoring (Sentry, New Relic, etc.)
- [ ] Regular security updates
- [ ] Database backups configured

## Deployment Complete!

Your Stock Research Platform is now deployed and running in production.

Access your site at: https://yourdomain.com
Admin panel: https://yourdomain.com/admin/
