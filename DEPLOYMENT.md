# VoteWise2 Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Database Setup](#database-setup)
4. [Application Deployment](#application-deployment)
5. [Web Server Configuration](#web-server-configuration)
6. [SSL/TLS Setup](#ssltls-setup)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

### Required Software
- Ubuntu 20.04 LTS or later (recommended)
- Python 3.9 or later
- PostgreSQL 13 or later
- Nginx
- Git

### Required Access
- SSH access to production server
- Domain name configured
- SSL certificate (Let's Encrypt recommended)

---

## Server Setup

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Required Packages
```bash
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx git
```

### 3. Create Application User
```bash
sudo useradd -m -s /bin/bash votewise
sudo usermod -aG sudo votewise
```

---

## Database Setup

### 1. Create PostgreSQL Database
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE votewise_db;
CREATE USER votewise_user WITH PASSWORD 'your_secure_password';
ALTER ROLE votewise_user SET client_encoding TO 'utf8';
ALTER ROLE votewise_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE votewise_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE votewise_db TO votewise_user;
\q
```

### 2. Test Database Connection
```bash
psql -h localhost -U votewise_user -d votewise_db
```

---

## Application Deployment

### 1. Clone Repository
```bash
cd /var/www
sudo git clone https://github.com/your-repo/VoteWise2.git votewise
sudo chown -R votewise:votewise /var/www/votewise
cd /var/www/votewise
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
nano .env
```

Fill in production values:
```env
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com

DB_NAME=votewise_db
DB_USER=votewise_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@your-domain.com
```

### 5. Run Pre-Deployment Checks
```bash
chmod +x scripts/*.sh
./scripts/pre_deploy_check.sh
```

### 6. Run Migrations
```bash
python manage.py migrate --settings=project_config.settings.production
```

### 7. Collect Static Files
```bash
python manage.py collectstatic --settings=project_config.settings.production --noinput
```

### 8. Create Superuser
```bash
python manage.py createsuperuser --settings=project_config.settings.production
```

---

## Web Server Configuration

### 1. Configure Gunicorn Service
```bash
sudo cp deploy/votewise.service /etc/systemd/system/
sudo nano /etc/systemd/system/votewise.service
```

Update paths in the service file, then:
```bash
sudo systemctl daemon-reload
sudo systemctl start votewise
sudo systemctl enable votewise
sudo systemctl status votewise
```

### 2. Configure Nginx
```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/votewise
sudo nano /etc/nginx/sites-available/votewise
```

Update domain and paths, then:
```bash
sudo ln -s /etc/nginx/sites-available/votewise /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## SSL/TLS Setup

### Using Let's Encrypt (Recommended)

### 1. Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx
```

### 2. Obtain Certificate
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 3. Auto-Renewal
Certbot automatically sets up renewal. Test it:
```bash
sudo certbot renew --dry-run
```

---

## Monitoring & Maintenance

### Health Check
```bash
curl https://your-domain.com/health/
```

### View Logs
```bash
# Application logs
tail -f /var/www/votewise/logs/gunicorn_error.log

# Nginx logs
sudo tail -f /var/log/nginx/votewise_error.log

# System logs
sudo journalctl -u votewise -f
```

### Database Backup
Set up automated backups:
```bash
# Add to crontab
crontab -e

# Add this line for daily backups at 2 AM
0 2 * * * /var/www/votewise/scripts/backup_db.sh
```

### Deployment Updates
```bash
cd /var/www/votewise
./scripts/deploy.sh --pull
```

---

## Troubleshooting

### Application Won't Start
```bash
# Check logs
sudo journalctl -u votewise -n 50

# Check permissions
ls -la /var/www/votewise

# Verify environment variables
sudo systemctl show votewise | grep Environment
```

### Static Files Not Loading
```bash
# Recollect static files
python manage.py collectstatic --clear --noinput --settings=project_config.settings.production

# Check nginx configuration
sudo nginx -t

# Verify file permissions
ls -la /var/www/votewise/staticfiles
```

### Database Connection Issues
```bash
# Test connection
psql -h localhost -U votewise_user -d votewise_db

# Check PostgreSQL status
sudo systemctl status postgresql
```

---

## Security Checklist

- [ ] Firewall configured (UFW)
- [ ] SSH key-based authentication only
- [ ] PostgreSQL only accepts local connections
- [ ] Regular security updates enabled
- [ ] Fail2ban installed and configured
- [ ] Database backups automated
- [ ] SSL certificate auto-renewal working
- [ ] Application logs monitored
- [ ] Health checks configured

---

## Support

For issues or questions:
1. Check application logs
2. Review Django deployment checklist: `python manage.py check --deploy`
3. Consult Django documentation
4. Check project documentation

---

**Last Updated**: 2025-11-26
