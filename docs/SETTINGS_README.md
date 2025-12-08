# VoteWise2 - Django Settings Configuration Guide

## Settings Structure

The project now uses a split settings configuration:

```
project_config/
├── settings/
│   ├── __init__.py      # Defaults to development
│   ├── base.py          # Common settings for all environments
│   ├── development.py   # Development-specific settings
│   └── production.py    # Production-specific settings
```

## Development Usage

By default, the project uses development settings:

```bash
# Standard development server
python manage.py runserver

# Or explicitly specify development settings
python manage.py runserver --settings=project_config.settings.development
```

## Production Usage

For production deployment, set the `DJANGO_SETTINGS_MODULE` environment variable:

```bash
# Set environment variable
export DJANGO_SETTINGS_MODULE=project_config.settings.production

# Or specify in command
python manage.py migrate --settings=project_config.settings.production
gunicorn project_config.wsgi --env DJANGO_SETTINGS_MODULE=project_config.settings.production
```

## Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual values

3. **NEVER commit `.env` to version control!**

## Key Differences

### Development Settings
- `DEBUG = True`
- SQLite database
- Console email backend
- Permissive ALLOWED_HOSTS
- No HTTPS enforcement

### Production Settings
- `DEBUG = False`
- PostgreSQL database (required)
- SMTP email backend
- Strict ALLOWED_HOSTS (must be set)
- Full security headers (HTTPS, HSTS, etc.)
- File-based error logging
- Session security hardening

## Production Deployment Checklist

Before deploying to production:

1. ✅ Set all required environment variables in `.env`
2. ✅ Generate a new SECRET_KEY
3. ✅ Set up PostgreSQL database
4. ✅ Configure ALLOWED_HOSTS
5. ✅ Configure email settings
6. ✅ Run migrations: `python manage.py migrate --settings=project_config.settings.production`
7. ✅ Collect static files: `python manage.py collectstatic --settings=project_config.settings.production`
8. ✅ Create superuser: `python manage.py createsuperuser --settings=project_config.settings.production`
9. ✅ Set up HTTPS/SSL certificates
10. ✅ Configure web server (Nginx/Apache)
11. ✅ Set up WSGI server (Gunicorn/uWSGI)

## Generating a New SECRET_KEY

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
