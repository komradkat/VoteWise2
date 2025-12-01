# VoteWise2 - Production Deployment Checklist

## Pre-Deployment Checklist

### 1. Environment Setup ✅

- [ ] **Server Requirements Met**
  - [ ] Python 3.13+ installed
  - [ ] 2GB+ RAM available
  - [ ] 10GB+ storage available
  - [ ] 2+ CPU cores
  - [ ] Ubuntu 20.04+ or similar Linux distribution

- [ ] **Domain & SSL**
  - [ ] Domain name registered
  - [ ] DNS configured
  - [ ] SSL certificate obtained (Let's Encrypt recommended)
  - [ ] HTTPS configured

### 2. Database Setup ✅

- [ ] **Production Database**
  - [ ] PostgreSQL 14+ installed (recommended)
  - [ ] Database created
  - [ ] Database user created with proper permissions
  - [ ] Database connection tested
  - [ ] Backup strategy configured

```sql
-- PostgreSQL setup example
CREATE DATABASE votewise_prod;
CREATE USER votewise_user WITH PASSWORD 'strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE votewise_prod TO votewise_user;
```

### 3. Application Configuration ✅

- [ ] **Environment Variables (.env)**
  ```bash
  # Generate SECRET_KEY
  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
  ```
  
  - [ ] `SECRET_KEY` - Generated strong 50+ character key
  - [ ] `DEBUG=False` - CRITICAL: Must be False in production
  - [ ] `ALLOWED_HOSTS` - Your domain(s)
  - [ ] `DATABASE_URL` - Production database connection
  - [ ] `EMAIL_HOST` - SMTP server
  - [ ] `EMAIL_HOST_USER` - Email username
  - [ ] `EMAIL_HOST_PASSWORD` - Email password
  - [ ] `GEMINI_API_KEY` - For AI chatbot (optional)

- [ ] **Security Settings**
  - [ ] `SECURE_HSTS_SECONDS=31536000`
  - [ ] `SECURE_SSL_REDIRECT=True`
  - [ ] `SESSION_COOKIE_SECURE=True`
  - [ ] `CSRF_COOKIE_SECURE=True`
  - [ ] `SECURE_BROWSER_XSS_FILTER=True`
  - [ ] `SECURE_CONTENT_TYPE_NOSNIFF=True`

### 4. Dependencies Installation ✅

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install database driver
pip install psycopg2-binary  # For PostgreSQL
# or
pip install mysqlclient  # For MySQL
```

- [ ] All requirements installed
- [ ] Database driver installed
- [ ] No installation errors

### 5. Static & Media Files ✅

```bash
# Create directories
mkdir -p staticfiles media logs

# Collect static files
python manage.py collectstatic --noinput

# Set permissions
chmod 755 staticfiles media logs
```

- [ ] Static files collected
- [ ] Media directory created
- [ ] Logs directory created
- [ ] Proper permissions set

### 6. Database Migrations ✅

```bash
# Run migrations
python manage.py migrate

# Verify migrations
python manage.py showmigrations
```

- [ ] All migrations applied
- [ ] No migration errors
- [ ] Database schema verified

### 7. Admin User Creation ✅

```bash
# Create superuser
python manage.py createsuperuser
```

- [ ] Superuser created
- [ ] Admin credentials documented (securely)
- [ ] Admin login tested

### 8. Application Testing ✅

```bash
# Run Django check
python manage.py check --deploy

# Test server startup
gunicorn project_config.wsgi:application --bind 127.0.0.1:8000
```

- [ ] Django deployment check passed
- [ ] Gunicorn starts successfully
- [ ] No startup errors

### 9. Web Server Configuration (Nginx) ✅

Create `/etc/nginx/sites-available/votewise`:

```nginx
upstream votewise {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 10M;

    location /static/ {
        alias /path/to/VoteWise2/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/VoteWise2/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://votewise;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

- [ ] Nginx configuration created
- [ ] SSL certificates configured
- [ ] Configuration tested (`nginx -t`)
- [ ] Nginx reloaded

### 10. Systemd Service (Gunicorn) ✅

Create `/etc/systemd/system/votewise.service`:

```ini
[Unit]
Description=VoteWise2 Gunicorn Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/VoteWise2
Environment="PATH=/path/to/VoteWise2/.venv/bin"
ExecStart=/path/to/VoteWise2/.venv/bin/gunicorn \
          --workers 4 \
          --bind 127.0.0.1:8000 \
          --timeout 120 \
          --access-logfile /path/to/VoteWise2/logs/gunicorn-access.log \
          --error-logfile /path/to/VoteWise2/logs/gunicorn-error.log \
          project_config.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable votewise
sudo systemctl start votewise
sudo systemctl status votewise
```

- [ ] Systemd service created
- [ ] Service enabled
- [ ] Service started
- [ ] Service status verified

### 11. Firewall Configuration ✅

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

- [ ] Firewall configured
- [ ] Only necessary ports open
- [ ] SSH access maintained

### 12. Monitoring & Logging ✅

- [ ] **Application Logs**
  - [ ] Log directory writable
  - [ ] Log rotation configured
  - [ ] Logs being generated

- [ ] **Server Monitoring** (Optional)
  - [ ] Sentry configured
  - [ ] Uptime monitoring
  - [ ] Error alerting

### 13. Backup Strategy ✅

```bash
# Database backup script
#!/bin/bash
BACKUP_DIR="/backups/votewise"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump votewise_prod > $BACKUP_DIR/db_backup_$DATE.sql
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete
```

- [ ] Database backup script created
- [ ] Backup cron job configured
- [ ] Backup restoration tested
- [ ] Media files backup configured

### 14. Security Hardening ✅

- [ ] **Server Security**
  - [ ] SSH key-based authentication only
  - [ ] Root login disabled
  - [ ] Fail2ban installed and configured
  - [ ] Automatic security updates enabled

- [ ] **Application Security**
  - [ ] All security settings enabled
  - [ ] HTTPS enforced
  - [ ] Security headers configured
  - [ ] Rate limiting considered

### 15. Performance Optimization ✅

- [ ] **Caching** (Optional but recommended)
  - [ ] Redis installed
  - [ ] Django cache configured
  - [ ] Session caching enabled

- [ ] **Database**
  - [ ] Database indexes verified
  - [ ] Connection pooling configured
  - [ ] Query optimization reviewed

### 16. Final Testing ✅

- [ ] **Functionality Testing**
  - [ ] User registration works
  - [ ] Login works (password and face)
  - [ ] Voting works
  - [ ] Admin panel accessible
  - [ ] Email notifications sent
  - [ ] PDF reports generated
  - [ ] AI chatbot responds

- [ ] **Security Testing**
  - [ ] HTTPS enforced
  - [ ] Security headers present
  - [ ] CSRF protection working
  - [ ] SQL injection prevented
  - [ ] XSS protection working

- [ ] **Performance Testing**
  - [ ] Page load times acceptable
  - [ ] Database queries optimized
  - [ ] Static files served correctly
  - [ ] Face recognition responsive

### 17. Documentation ✅

- [ ] **Admin Documentation**
  - [ ] Server access credentials documented
  - [ ] Database credentials documented
  - [ ] Email credentials documented
  - [ ] API keys documented
  - [ ] Backup procedures documented

- [ ] **User Documentation**
  - [ ] User guide created
  - [ ] Admin guide created
  - [ ] FAQ prepared

### 18. Go-Live Checklist ✅

- [ ] **Pre-Launch**
  - [ ] All tests passed
  - [ ] Backup verified
  - [ ] Monitoring active
  - [ ] Support team briefed

- [ ] **Launch**
  - [ ] DNS updated to production server
  - [ ] SSL certificate verified
  - [ ] Application accessible
  - [ ] All features working

- [ ] **Post-Launch**
  - [ ] Monitor logs for errors
  - [ ] Monitor server resources
  - [ ] User feedback collected
  - [ ] Performance metrics tracked

---

## Quick Deployment Commands

```bash
# 1. Clone and setup
git clone <repo-url> /var/www/votewise
cd /var/www/votewise
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
pip install psycopg2-binary gunicorn

# 3. Configure environment
cp .env.example .env
nano .env  # Edit with production values

# 4. Setup database
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput

# 5. Create directories
mkdir -p logs staticfiles media
chmod 755 logs staticfiles media

# 6. Test
python manage.py check --deploy
gunicorn project_config.wsgi:application --bind 127.0.0.1:8000

# 7. Setup systemd service
sudo cp votewise.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable votewise
sudo systemctl start votewise

# 8. Setup Nginx
sudo cp nginx.conf /etc/nginx/sites-available/votewise
sudo ln -s /etc/nginx/sites-available/votewise /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 9. Setup SSL
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 10. Verify
sudo systemctl status votewise
sudo systemctl status nginx
curl https://yourdomain.com
```

---

## Troubleshooting

### Application won't start
```bash
# Check logs
sudo journalctl -u votewise -n 50
tail -f logs/gunicorn-error.log

# Check permissions
ls -la /var/www/votewise
```

### Static files not loading
```bash
# Recollect static files
python manage.py collectstatic --noinput --clear

# Check Nginx configuration
sudo nginx -t
```

### Database connection errors
```bash
# Test database connection
python manage.py dbshell

# Check database credentials in .env
cat .env | grep DATABASE
```

### SSL certificate issues
```bash
# Renew certificate
sudo certbot renew

# Test SSL
sudo certbot certificates
```

---

## Maintenance Tasks

### Daily
- Monitor application logs
- Check server resources (CPU, RAM, disk)
- Verify backups completed

### Weekly
- Review error logs
- Check for security updates
- Monitor user activity

### Monthly
- Update dependencies (security patches)
- Review and optimize database
- Test backup restoration
- Review performance metrics

---

## Emergency Contacts

- **Server Admin**: [Contact Info]
- **Database Admin**: [Contact Info]
- **Application Support**: [Contact Info]
- **Hosting Provider**: [Contact Info]

---

## Rollback Plan

If deployment fails:

1. **Restore Database**
   ```bash
   psql votewise_prod < /backups/votewise/db_backup_YYYYMMDD.sql
   ```

2. **Revert Code**
   ```bash
   git checkout <previous-commit>
   sudo systemctl restart votewise
   ```

3. **Clear Cache**
   ```bash
   python manage.py clear_cache
   ```

---

**Deployment Date**: _______________  
**Deployed By**: _______________  
**Verified By**: _______________  
**Status**: _______________
