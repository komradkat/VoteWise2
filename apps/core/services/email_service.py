"""
Email Service for VoteWise2
Centralized email sending functionality with template support
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from apps.core.logging import logger


class EmailService:
    """
    Centralized email service for sending notifications
    Supports both HTML and plain text emails
    """
    
    @staticmethod
    def send_email(subject, template_name, context, recipient_list, from_email=None):
        """
        Send an email using HTML and plain text templates
        
        Args:
            subject (str): Email subject line
            template_name (str): Base name of template (without extension)
            context (dict): Context data for template rendering
            recipient_list (list): List of recipient email addresses
            from_email (str, optional): Sender email address
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not recipient_list:
            logger.email("No recipients provided for email")
            return False
            
        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL
            
        try:
            # Add common context variables
            context.update({
                'site_name': 'VoteWise',
                'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
            })
            
            # Render HTML template
            html_content = render_to_string(f'emails/{template_name}.html', context)
            
            # Render plain text template (or strip HTML as fallback)
            try:
                text_content = render_to_string(f'emails/{template_name}.txt', context)
            except:
                text_content = strip_tags(html_content)
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=recipient_list
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send(fail_silently=False)
            
            logger.email(f"Email sent successfully: {subject} to {len(recipient_list)} recipient(s)", extra_data={'subject': subject, 'recipient_count': len(recipient_list)})
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email '{subject}': {str(e)}", category="EMAIL", extra_data={'subject': subject, 'error': str(e)})
            return False
    
    @staticmethod
    def send_welcome_email(user):
        """
        Send welcome email to newly registered user
        
        Args:
            user: User object
            
        Returns:
            bool: True if sent successfully
        """
        subject = "Welcome to VoteWise!"
        template_name = "welcome"
        context = {
            'user': user,
            'username': user.get_full_name() or user.username,
        }
        
        return EmailService.send_email(
            subject=subject,
            template_name=template_name,
            context=context,
            recipient_list=[user.email]
        )
    
    @staticmethod
    def send_vote_confirmation(voter, election):
        """
        Send vote confirmation receipt to voter
        
        Args:
            voter: User object who voted
            election: Election object
            
        Returns:
            bool: True if sent successfully
        """
        from datetime import datetime
        
        subject = f"Vote Confirmation - {election.name}"
        template_name = "vote_confirmation"
        context = {
            'voter': voter,
            'voter_name': voter.get_full_name() or voter.username,
            'election': election,
            'timestamp': datetime.now(),
        }
        
        return EmailService.send_email(
            subject=subject,
            template_name=template_name,
            context=context,
            recipient_list=[voter.email]
        )
    
    @staticmethod
    def send_election_notification(election, notification_type='started'):
        """
        Send election start/end notification to eligible voters
        
        Args:
            election: Election object
            notification_type (str): 'started' or 'ended'
            
        Returns:
            int: Number of emails sent successfully
        """
        from apps.accounts.models import User
        
        # Get all active users (eligible voters)
        voters = User.objects.filter(is_active=True).exclude(email='')
        
        if notification_type == 'started':
            subject = f"Election Started: {election.name}"
            template_name = "election_start"
        else:
            subject = f"Election Ended: {election.name}"
            template_name = "election_end"
        
        sent_count = 0
        for voter in voters:
            context = {
                'voter': voter,
                'voter_name': voter.get_full_name() or voter.username,
                'election': election,
            }
            
            if EmailService.send_email(
                subject=subject,
                template_name=template_name,
                context=context,
                recipient_list=[voter.email]
            ):
                sent_count += 1
        
        logger.email(f"Sent {sent_count} election {notification_type} notifications for '{election.name}'", extra_data={'election_id': election.id, 'notification_type': notification_type, 'sent_count': sent_count})
        return sent_count
    
    @staticmethod
    def send_results_announcement(election):
        """
        Send election results announcement to participants
        
        Args:
            election: Election object
            
        Returns:
            int: Number of emails sent successfully
        """
        from apps.elections.models import VoterReceipt
        
        # Get all voters who participated in this election
        voter_receipts = VoterReceipt.objects.filter(election=election).select_related('voter')
        voters = [receipt.voter for receipt in voter_receipts]
        
        subject = f"Results Available: {election.name}"
        template_name = "results_announcement"
        
        sent_count = 0
        for voter in voters:
            if not voter.email:
                continue
                
            context = {
                'voter': voter,
                'voter_name': voter.get_full_name() or voter.username,
                'election': election,
            }
            
            if EmailService.send_email(
                subject=subject,
                template_name=template_name,
                context=context,
                recipient_list=[voter.email]
            ):
                sent_count += 1
        
        logger.email(f"Sent {sent_count} results announcements for '{election.name}'", extra_data={'election_id': election.id, 'sent_count': sent_count})
        return sent_count
    
    @staticmethod
    def send_password_reset_email(user, reset_url):
        """
        Send password reset email with secure link
        
        Args:
            user: User object
            reset_url (str): Password reset URL with token
            
        Returns:
            bool: True if sent successfully
        """
        subject = "Password Reset Request - VoteWise"
        template_name = "password_reset"
        context = {
            'user': user,
            'username': user.get_full_name() or user.username,
            'reset_url': reset_url,
        }
        
        return EmailService.send_email(
            subject=subject,
            template_name=template_name,
            context=context,
            recipient_list=[user.email]
        )
    
    @staticmethod
    def send_admin_notification(subject, message, admin_emails=None):
        """
        Send notification to administrators
        
        Args:
            subject (str): Email subject
            message (str): Email message
            admin_emails (list, optional): List of admin emails
            
        Returns:
            bool: True if sent successfully
        """
        from apps.accounts.models import User
        
        if admin_emails is None:
            # Get all superuser emails
            admins = User.objects.filter(is_superuser=True, is_active=True).exclude(email='')
            admin_emails = [admin.email for admin in admins]
        
        if not admin_emails:
            logger.email("No admin emails found for notification")
            return False
        
        template_name = "admin_notification"
        context = {
            'subject': subject,
            'message': message,
        }
        
        return EmailService.send_email(
            subject=f"[VoteWise Admin] {subject}",
            template_name=template_name,
            context=context,
            recipient_list=admin_emails
        )
    
    @staticmethod
    def send_bulk_email(subject, message, recipient_list):
        """
        Send bulk email to multiple recipients
        
        Args:
            subject (str): Email subject
            message (str): Email message (HTML supported)
            recipient_list (list): List of recipient emails
            
        Returns:
            int: Number of emails sent successfully
        """
        template_name = "bulk_email"
        sent_count = 0
        
        for recipient in recipient_list:
            context = {
                'message': message,
            }
            
            if EmailService.send_email(
                subject=subject,
                template_name=template_name,
                context=context,
                recipient_list=[recipient]
            ):
                sent_count += 1
        
        logger.email(f"Sent {sent_count}/{len(recipient_list)} bulk emails", extra_data={'sent_count': sent_count, 'total_recipients': len(recipient_list)})
        return sent_count
