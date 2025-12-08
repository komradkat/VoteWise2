"""
Gunicorn configuration file for VoteWise2
"""
import multiprocessing
import os

# Server socket
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
backlog = 2048

# Worker processes
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = os.getenv('GUNICORN_ACCESS_LOG', 'logs/gunicorn_access.log')
errorlog = os.getenv('GUNICORN_ERROR_LOG', 'logs/gunicorn_error.log')
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')

# Process naming
proc_name = 'votewise'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Reload on code changes (disable in production)
reload = os.getenv('GUNICORN_RELOAD', 'False') == 'True'
