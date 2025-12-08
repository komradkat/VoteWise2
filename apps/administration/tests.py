from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.accounts.models import StudentProfile, ElectionAdmin
from apps.elections.models import Election

class AdminDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create regular user
        self.user = User.objects.create_user(username='user', password='password')
        self.student_profile = StudentProfile.objects.create(user=self.user, student_id='123', year_level=1)
        
        # Create admin user
        self.admin_user = User.objects.create_user(username='admin', password='password')
        # ElectionAdmin links directly to User, not StudentProfile
        self.election_admin = ElectionAdmin.objects.create(user=self.admin_user, admin_type='EMP')
        
        self.dashboard_url = reverse('administration:dashboard')
        self.election_list_url = reverse('administration:elections')

    def test_admin_access_denied_for_anonymous(self):
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f'/administration/login/?next={self.dashboard_url}')

    def test_admin_access_denied_for_regular_user(self):
        self.client.login(username='user', password='password')
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f'/administration/login/?next={self.dashboard_url}', target_status_code=302)

    def test_admin_access_granted_for_admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/dashboard.html')

    def test_election_crud(self):
        self.client.login(username='admin', password='password')
        
        # Create
        create_url = reverse('administration:election_create')
        data = {
            'name': 'Test Election',
            'start_time': '2025-01-01T00:00',
            'end_time': '2025-01-02T00:00',
            'is_active': True
        }
        response = self.client.post(create_url, data)
        self.assertRedirects(response, self.election_list_url)
        self.assertEqual(Election.objects.count(), 1)
        
        # Read
        response = self.client.get(self.election_list_url)
        self.assertContains(response, 'Test Election')
        
        # Update
        election = Election.objects.first()
        edit_url = reverse('administration:election_edit', args=[election.pk])
        data['name'] = 'Updated Election'
        response = self.client.post(edit_url, data)
        self.assertRedirects(response, self.election_list_url)
        
        election.refresh_from_db()
        self.assertEqual(election.name, 'Updated Election')
