"""
Unit tests for Email Service
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from apps.core.services.email_service import EmailService
from apps.elections.models import Election
from datetime import datetime, timedelta

User = get_user_model()


class EmailServiceTests(TestCase):
    """Test cases for EmailService"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.election = Election.objects.create(
            name='Test Election 2025',
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(days=7),
            is_active=True
        )
    
    def test_send_welcome_email(self):
        """Test welcome email sends correctly"""
        result = EmailService.send_welcome_email(self.user)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Check email content
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Welcome to VoteWise!')
        self.assertIn(self.user.email, email.to)
        self.assertIn('Test User', email.body)
    
    def test_send_vote_confirmation(self):
        """Test vote confirmation email"""
        result = EmailService.send_vote_confirmation(self.user, self.election)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Check email content
        email = mail.outbox[0]
        self.assertIn('Vote Confirmation', email.subject)
        self.assertIn(self.election.name, email.subject)
        self.assertIn(self.user.email, email.to)
    
    def test_send_email_with_no_recipients(self):
        """Test email sending with empty recipient list"""
        result = EmailService.send_email(
            subject='Test',
            template_name='welcome',
            context={},
            recipient_list=[]
        )
        
        # Should return False and not send
        self.assertFalse(result)
        self.assertEqual(len(mail.outbox), 0)
    
    def test_send_election_notification(self):
        """Test election notification sends to active users"""
        # Create additional users
        User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        sent_count = EmailService.send_election_notification(
            self.election,
            notification_type='started'
        )
        
        # Should send to all active users with emails
        self.assertEqual(sent_count, 2)
        self.assertEqual(len(mail.outbox), 2)
    
    def test_send_admin_notification(self):
        """Test admin notification"""
        # Create superuser
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        result = EmailService.send_admin_notification(
            subject='Test Alert',
            message='This is a test admin notification'
        )
        
        # Check email was sent
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertIn('[VoteWise Admin]', email.subject)
        self.assertIn(admin.email, email.to)
