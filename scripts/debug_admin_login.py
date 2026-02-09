import os
import django
from django.conf import settings

import sys
from pathlib import Path

# Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_config.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from apps.accounts.models import ElectionAdmin

def check_admin_login():
    # Setup
    username = 'debug_admin'
    password = 'password'
    if User.objects.filter(username=username).exists():
        User.objects.filter(username=username).delete()
    
    user = User.objects.create_user(username=username, password=password)
    admin_profile = ElectionAdmin.objects.create(user=user, admin_type='EMP')
    
    print(f"Created admin user: {username}")
    
    client = Client()
    login_success = client.login(username=username, password=password)
    print(f"Login success: {login_success}")
    
    if not login_success:
        print("Login failed!")
        return
        
    response = client.get('/administration/')
    print(f"Dashboard response code: {response.status_code}")
    if response.status_code == 302:
        print(f"Redirected to: {response.url}")
    elif response.status_code != 200:
        print("Dashboard failed to load.")
    else:
        print("Dashboard loaded successfully.")

if __name__ == '__main__':
    check_admin_login()
