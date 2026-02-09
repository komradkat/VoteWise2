from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.accounts.models import StudentProfile, ElectionAdmin

class AdminLoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('administration:login')
        self.dashboard_url = reverse('administration:dashboard')
        
        # Create admin user
        self.admin_user = User.objects.create_user(username='admin', password='password')
        self.election_admin = ElectionAdmin.objects.create(user=self.admin_user, admin_type='EMP')
        
        # Create regular user
        self.user = User.objects.create_user(username='user', password='password')

    def test_admin_login_page_loads(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/login.html')

    def test_admin_login_success(self):
        response = self.client.post(self.login_url, {
            'username': 'admin',
            'password': 'password'
        })
        self.assertRedirects(response, self.dashboard_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_regular_user_login_denied(self):
        response = self.client.post(self.login_url, {
            'username': 'user',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200) # Should stay on page with error
        self.assertContains(response, "Access denied")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_redirect_to_admin_login(self):
        # Accessing dashboard without login should redirect to admin login, not standard login
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f'/administration/login/?next={self.dashboard_url}')

    def test_superuser_login_success(self):
        # Create a superuser who doesn't have an ElectionAdmin profile
        superuser = User.objects.create_superuser(username='superuser', password='password', email='super@example.com')
        response = self.client.post(self.login_url, {
            'username': 'superuser',
            'password': 'password'
        })
        self.assertRedirects(response, self.dashboard_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_dashboard_stats_context(self):
        # Log in as admin
        self.client.force_login(self.admin_user)
        response = self.client.get(self.dashboard_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_voters', response.context)
        self.assertIn('all_elections', response.context) # Updated from active_elections
        self.assertIn('total_candidates', response.context)
        self.assertIn('total_votes', response.context)
        self.assertIn('course_labels', response.context)
        self.assertIn('course_counts', response.context)
        self.assertIn('year_labels', response.context)
        self.assertIn('year_counts', response.context)
        
        # Check values (should be 0 initially based on setup)
        self.assertEqual(response.context['total_voters'], 0)
