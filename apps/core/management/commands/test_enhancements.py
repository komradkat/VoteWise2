#!/usr/bin/env python
"""
VoteWise2 Comprehensive Testing Script
Run with: python manage.py shell < test_enhancements.py
"""

print("=" * 60)
print("VoteWise2 Comprehensive Testing")
print("=" * 60)

# Test 1: Form Imports
print("\n[TEST 1] Form Imports")
try:
    from apps.administration.forms import (
        ElectionForm, CandidateForm, VoterForm, ElectionAdminForm
    )
    print("✓ All forms imported successfully")
except Exception as e:
    print(f"✗ Form import failed: {e}")

# Test 2: ElectionAdminForm Enhancements
print("\n[TEST 2] ElectionAdminForm Enhancements")
try:
    form = ElectionAdminForm()
    assert 'student_profile' in form.fields, "student_profile field missing"
    assert 'confirm_password' in form.fields, "confirm_password field missing"
    assert form.fields['password'].required == False, "password should be optional"
    print("✓ student_profile field exists")
    print("✓ confirm_password field exists")
    print("✓ password field is optional")
except Exception as e:
    print(f"✗ ElectionAdminForm test failed: {e}")

# Test 3: URL Routing
print("\n[TEST 3] URL Routing")
try:
    from django.urls import reverse
    
    urls_to_test = {
        'administration:dashboard': '/administration/',
        'administration:election_create': '/administration/elections/create/',
        'administration:candidate_create': '/administration/candidates/create/',
        'administration:voter_create': '/administration/voters/create/',
        'administration:administrator_create': '/administration/administrators/create/',
        'administration:api_student_profile': '/administration/api/student-profile/1/',
    }
    
    for url_name, expected_path in urls_to_test.items():
        try:
            if 'api_student_profile' in url_name:
                url = reverse(url_name, args=[1])
            else:
                url = reverse(url_name)
            print(f"✓ {url_name}: {url}")
        except Exception as e:
            print(f"✗ {url_name}: {e}")
            
except Exception as e:
    print(f"✗ URL routing test failed: {e}")

# Test 4: API View Function
print("\n[TEST 4] API View Function")
try:
    from apps.administration.views import get_student_profile_data
    print("✓ get_student_profile_data view exists")
except Exception as e:
    print(f"✗ API view test failed: {e}")

# Test 5: Model Integrity
print("\n[TEST 5] Model Integrity")
try:
    from apps.accounts.models import StudentProfile, ElectionAdmin, AdminType
    from apps.elections.models import Election, Candidate
    
    print(f"✓ StudentProfile model loaded")
    print(f"✓ ElectionAdmin model loaded")
    print(f"✓ AdminType choices: {list(AdminType.choices)}")
    print(f"✓ Election model loaded")
    print(f"✓ Candidate model loaded")
except Exception as e:
    print(f"✗ Model integrity test failed: {e}")

# Test 6: Template Files Exist
print("\n[TEST 6] Template Files")
try:
    import os
    from django.conf import settings
    
    templates_to_check = [
        'apps/administration/templates/administration/forms/election_form.html',
        'apps/administration/templates/administration/forms/candidate_form.html',
        'apps/administration/templates/administration/forms/voter_form.html',
        'apps/administration/templates/administration/forms/admin_form.html',
    ]
    
    for template_path in templates_to_check:
        full_path = os.path.join(settings.BASE_DIR, template_path)
        if os.path.exists(full_path):
            print(f"✓ {os.path.basename(template_path)} exists")
        else:
            print(f"✗ {os.path.basename(template_path)} missing")
            
except Exception as e:
    print(f"✗ Template check failed: {e}")

# Test 7: CSS Files Exist
print("\n[TEST 7] CSS Files")
try:
    css_files_to_check = [
        'apps/administration/static/administration/css/forms/election_form.css',
        'apps/administration/static/administration/css/forms/candidate_form.css',
        'apps/administration/static/administration/css/forms/voter_form.css',
        'apps/administration/static/administration/css/forms/admin_form.css',
    ]
    
    for css_path in css_files_to_check:
        full_path = os.path.join(settings.BASE_DIR, css_path)
        if os.path.exists(full_path):
            print(f"✓ {os.path.basename(css_path)} exists")
        else:
            print(f"✗ {os.path.basename(css_path)} missing")
            
except Exception as e:
    print(f"✗ CSS check failed: {e}")

print("\n" + "=" * 60)
print("Testing Complete")
print("=" * 60)
