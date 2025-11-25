# Production Deployment Checklist

Use this checklist before deploying VoteWise2 to production.

## Pre-Deployment

### Environment Configuration
- [ ] `.env` file created from `.env.example`
- [ ] `SECRET_KEY` generated (use: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
- [ ] `DEBUG=False` set in `.env`
- [ ] `ALLOWED_HOSTS` configured with actual domain(s)
- [ ] `CSRF_TRUSTED_ORIGINS` configured with HTTPS URLs
- [ ] Database credentials configured
- [ ] Email settings configured

### Database
- [ ] PostgreSQL installed and running
- [ ] Database created
- [ ] Database user created with proper permissions
- [ ] Database connection tested
- [ ] Migrations run successfully
- [ ] Superuser account created

### Dependencies
- [ ] All requirements installed: `pip install -r requirements.txt`
- [ ] Virtual environment activated
- [ ] Python version verified (3.9+)

### Static Files
- [ ] `STATIC_ROOT` configured in production settings
- [ ] Static files collected: `python manage.py collectstatic`
- [ ] Static files directory permissions correct
- [ ] Whitenoise configured in middleware

### Security
- [ ] Django deployment check passed: `python manage.py check --deploy`
- [ ] HTTPS configured
- [ ] SSL certificate installed
- [ ] Security headers configured
- [ ] HSTS enabled
- [ ] Secure cookies enabled
- [ ] CSRF protection verified

## Infrastructure

### Server Setup
- [ ] Server OS updated
- [ ] Required packages installed (Python, PostgreSQL, Nginx)
- [ ] Application user created
- [ ] Application directory created with correct permissions
- [ ] Logs directory created: `mkdir -p logs`
- [ ] Backups directory created: `mkdir -p backups`

### Web Server
- [ ] Nginx installed
- [ ] Nginx configuration file created
- [ ] Nginx configuration tested: `sudo nginx -t`
- [ ] Nginx enabled and running
- [ ] Firewall configured (ports 80, 443 open)

### Application Server
- [ ] Gunicorn installed
- [ ] Gunicorn configuration file created
- [ ] Systemd service file created
- [ ] Service enabled: `sudo systemctl enable votewise`
- [ ] Service running: `sudo systemctl status votewise`

### SSL/TLS
- [ ] SSL certificate obtained
- [ ] Certificate auto-renewal configured
- [ ] HTTPS redirect working
- [ ] SSL test passed (ssllabs.com)

## Application

### Code
- [ ] Latest code deployed
- [ ] All migrations applied
- [ ] No pending migrations
- [ ] Admin interface accessible
- [ ] Health check endpoint responding: `/health/`

### Testing
- [ ] Application loads successfully
- [ ] Login functionality works
- [ ] Admin panel accessible
- [ ] Static files loading correctly
- [ ] Media files uploading/displaying correctly
- [ ] Email sending works
- [ ] Database queries working

## Monitoring & Maintenance

### Logging
- [ ] Application logs configured
- [ ] Nginx logs configured
- [ ] Log rotation configured
- [ ] Error notifications configured

### Backups
- [ ] Database backup script tested
- [ ] Automated backup schedule configured (cron)
- [ ] Backup restoration tested
- [ ] Backup retention policy set

### Monitoring
- [ ] Health check endpoint monitored
- [ ] Server resources monitored (CPU, RAM, disk)
- [ ] Application errors tracked
- [ ] Uptime monitoring configured

## Post-Deployment

### Verification
- [ ] Application accessible via domain
- [ ] HTTPS working correctly
- [ ] All pages loading
- [ ] Forms submitting correctly
- [ ] User registration working
- [ ] Email notifications sending
- [ ] Admin functions working

### Documentation
- [ ] Deployment documented
- [ ] Environment variables documented
- [ ] Backup/restore procedure documented
- [ ] Rollback procedure documented
- [ ] Team trained on deployment process

### Security
- [ ] Security scan completed
- [ ] Penetration testing completed (if required)
- [ ] Security headers verified
- [ ] OWASP top 10 reviewed

## Emergency Contacts

- **System Administrator**: _______________
- **Database Administrator**: _______________
- **Lead Developer**: _______________
- **Hosting Provider Support**: _______________

## Rollback Plan

If deployment fails:

1. Stop the application: `sudo systemctl stop votewise`
2. Restore previous code: `git checkout <previous-commit>`
3. Restore database backup (if needed)
4. Restart application: `sudo systemctl start votewise`
5. Verify rollback successful

## Sign-Off

- [ ] Technical Lead Approval: _________________ Date: _______
- [ ] Security Review: _________________ Date: _______
- [ ] Final Deployment: _________________ Date: _______

---

**Notes**:
- Keep this checklist updated with each deployment
- Document any issues encountered during deployment
- Review and improve checklist based on lessons learned
