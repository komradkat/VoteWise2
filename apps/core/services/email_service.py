"""
Email Service for VoteWise2
Centralized email sending functionality with template support.
Includes async threading for performance and bulk optimization.
"""
import threading
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from apps.core.logging import logger


class EmailService:
    """
    Centralized email service for sending notifications
    Supports both HTML and plain text emails
    Uses separate threads for non-blocking execution
    """
    
    @staticmethod
    def _send_thread(email_message):
        """Internal helper to send email in a separate thread"""
        try:
            email_message.send(fail_silently=False)
            logger.email(f"Async email sent successfully: {email_message.subject}")
        except Exception as e:
            logger.error(f"Async email failed '{email_message.subject}': {str(e)}", category="EMAIL_ASYNC")

    @staticmethod
    def _send_bulk_thread(messages):
        """Internal helper to send bulk emails in a separate thread using one connection"""
        try:
            connection = get_connection()
            connection.send_messages(messages)
            connection.close()
            logger.email(f"Async bulk batch sent: {len(messages)} emails")
        except Exception as e:
            logger.error(f"Async bulk send failed: {str(e)}", category="EMAIL_ASYNC_BULK")

    @staticmethod
    def send_email(subject, template_name, context, recipient_list, from_email=None, async_send=True):
        """
        Send an email using HTML and plain text templates
        
        Args:
            subject (str): Email subject line
            template_name (str): Base name of template (without extension)
            context (dict): Context data for template rendering
            recipient_list (list): List of recipient email addresses
            from_email (str, optional): Sender email address
            async_send (bool): Whether to send in a background thread
            
        Returns:
            bool: True if task scheduled (async) or email sent (sync)
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
            
            if async_send:
                thread = threading.Thread(target=EmailService._send_thread, args=(email,))
                thread.daemon = True  # ensuring it doesn't block program exit
                thread.start()
                return True
            else:
                email.send(fail_silently=False)
                logger.email(f"Email sent successfully: {subject} to {len(recipient_list)} recipient(s)")
                return True
            
        except Exception as e:
            logger.error(f"Failed to prepare/send email '{subject}': {str(e)}", category="EMAIL", extra_data={'subject': subject, 'error': str(e)})
            return False
    
    @staticmethod
    def send_welcome_email(user):
        """Send welcome email to newly registered user"""
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
        """Send vote confirmation receipt to voter"""
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
        Send election start/end notification to eligible voters using optimized bulk sending
        """
        from apps.accounts.models import User
        
        voters = User.objects.filter(is_active=True).exclude(email='')
        
        if notification_type == 'started':
            subject = f"Election Started: {election.name}"
            template_name = "election_start"
        else:
            subject = f"Election Ended: {election.name}"
            template_name = "election_end"
            
        # Prepare messages
        messages = []
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        from_email = settings.DEFAULT_FROM_EMAIL
        
        for voter in voters:
            context = {
                'voter': voter,
                'voter_name': voter.get_full_name() or voter.username,
                'election': election,
                'site_name': 'VoteWise',
                'site_url': site_url,
            }
            
            try:
                html_content = render_to_string(f'emails/{template_name}.html', context)
                try:
                    text_content = render_to_string(f'emails/{template_name}.txt', context)
                except:
                    text_content = strip_tags(html_content)
                    
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=from_email,
                    to=[voter.email]
                )
                email.attach_alternative(html_content, "text/html")
                messages.append(email)
            except Exception as e:
                logger.error(f"Error preparing bulk email for {voter.username}: {e}", category="EMAIL_BULK_PREP")
        
        # Send in background thread
        if messages:
             thread = threading.Thread(target=EmailService._send_bulk_thread, args=(messages,))
             thread.daemon = True
             thread.start()
        
        logger.email(f"Queued {len(messages)} election {notification_type} notifications for '{election.name}'")
        return len(messages)
    
    @staticmethod
    def send_results_announcement(election):
        """Send election results announcement to participants (Bulk)"""
        from apps.elections.models import VoterReceipt
        
        voter_receipts = VoterReceipt.objects.filter(election=election).select_related('voter')
        voters = [receipt.voter for receipt in voter_receipts]
        
        subject = f"Results Available: {election.name}"
        template_name = "results_announcement"
        
        messages = []
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        from_email = settings.DEFAULT_FROM_EMAIL
        
        for voter in voters:
            if not voter.email:
                continue
                
            context = {
                'voter': voter,
                'voter_name': voter.get_full_name() or voter.username,
                'election': election,
                'site_name': 'VoteWise',
                'site_url': site_url,
            }
            
            try:
                html_content = render_to_string(f'emails/{template_name}.html', context)
                try:
                    text_content = render_to_string(f'emails/{template_name}.txt', context)
                except:
                    text_content = strip_tags(html_content)
                    
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=from_email,
                    to=[voter.email]
                )
                email.attach_alternative(html_content, "text/html")
                messages.append(email)
            except Exception as e:
                 logger.error(f"Error preparing result email for {voter.username}: {e}", category="EMAIL_BULK_PREP")

        if messages:
             thread = threading.Thread(target=EmailService._send_bulk_thread, args=(messages,))
             thread.daemon = True
             thread.start()
             
        logger.email(f"Queued {len(messages)} results announcements for '{election.name}'")
        return len(messages)
    
    @staticmethod
    def send_password_reset_email(user, reset_url):
        """Send password reset email with secure link"""
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
        """Send notification to administrators"""
        from apps.accounts.models import User
        
        if admin_emails is None:
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
        """Send bulk email to multiple recipients"""
        template_name = "bulk_email"
        
        messages = []
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        from_email = settings.DEFAULT_FROM_EMAIL
        
        for recipient in recipient_list:
            context = {
                'message': message,
                'site_name': 'VoteWise',
                'site_url': site_url,
            }
            
            html_content = render_to_string(f'emails/{template_name}.html', context)
            try:
                text_content = render_to_string(f'emails/{template_name}.txt', context)
            except:
                text_content = strip_tags(html_content)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[recipient]
            )
            email.attach_alternative(html_content, "text/html")
            messages.append(email)
            
        if messages:
             thread = threading.Thread(target=EmailService._send_bulk_thread, args=(messages,))
             thread.daemon = True
             thread.start()
             
        logger.email(f"Queued {len(messages)} generic bulk emails")
        return len(messages)
