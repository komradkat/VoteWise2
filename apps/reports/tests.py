from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone


class DecoratorTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='password', is_staff=True)
        self.client = Client()
        self.client.force_login(self.user)

    def test_sudo_redirect(self):
        """Test that unverified session redirects to password verification."""
        # Clean session
        session = self.client.session
        if 'last_password_verified_at' in session:
            del session['last_password_verified_at']
            session.save()

        # We need to test a view that uses the decorator.
        # But reports_hub is protected by user_passes_test(is_admin) too.

        response = self.client.get('/reports/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/administration/verify-password/', response.url)

    def test_sudo_access(self):
        """Test that verified session allows access."""
        session = self.client.session
        session['last_password_verified_at'] = timezone.now().timestamp()
        session.save()

        response = self.client.get('/reports/')
        self.assertEqual(response.status_code, 200)

    def test_sudo_expiry(self):
        """Test that expired session redirects."""
        session = self.client.session
        # Set timestamp to 6 minutes ago
        session['last_password_verified_at'] = (timezone.now() - timezone.timedelta(minutes=6)).timestamp()
        session.save()

        response = self.client.get('/reports/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/administration/verify-password/', response.url)
