from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class AccountViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.login_url = reverse('accounts:login')
        self.profile_url = reverse('accounts:profile')

    def test_login_view_post(self):
        """Test that valid login redirects to profile."""
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'password'})
        self.assertRedirects(response, self.profile_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_profile_view_authenticated(self):
        """Test that profile view is accessible to logged-in users."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_profile_view_anonymous(self):
        """Test that profile view redirects anonymous users to login."""
        response = self.client.get(self.profile_url)
        self.assertRedirects(response, f'/auth/login/?next={self.profile_url}')

    def test_profile_view_context(self):
        """Test that profile view contains correct context data."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('user_form', response.context)
        self.assertIn('profile_form', response.context)
        self.assertIn('votes', response.context)

    def test_profile_update(self):
        """Test updating user profile."""
        self.client.login(username='testuser', password='password')
        data = {
            'username': 'testuser', # Readonly but sent in form
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
        }
        response = self.client.post(self.profile_url, data)
        self.assertRedirects(response, self.profile_url)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.email, 'updated@example.com')
