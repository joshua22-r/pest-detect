from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from .models import User, DetectionResult, Subscription
import logging

logger = logging.getLogger('api')


class EmailService:
    """Service for sending transactional and marketing emails"""

    @staticmethod
    def send_welcome_email(user):
        """Send welcome email to new user"""
        try:
            subject = 'Welcome to BioGuard AI - Your Pest Detection Companion!'
            context = {
                'user': user,
                'login_url': f"{settings.FRONTEND_URL}/auth/login",
                'year': timezone.now().year,
            }

            html_content = render_to_string('emails/welcome.html', context)
            text_content = strip_tags(html_content)

            EmailService._send_email(
                subject=subject,
                message=text_content,
                recipient_list=[user.email],
                html_message=html_content,
            )

            logger.info(f'Welcome email sent to {user.email}')

        except Exception as e:
            logger.error(f'Failed to send welcome email to {user.email}: {str(e)}')

    @staticmethod
    def send_password_reset_email(user, reset_token):
        """Send password reset email"""
        try:
            subject = 'BioGuard AI - Password Reset Request'
            reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={reset_token}"

            context = {
                'user': user,
                'reset_url': reset_url,
                'year': timezone.now().year,
            }

            html_content = render_to_string('emails/password_reset.html', context)
            text_content = strip_tags(html_content)

            EmailService._send_email(
                subject=subject,
                message=text_content,
                recipient_list=[user.email],
                html_message=html_content,
            )

            logger.info(f'Password reset email sent to {user.email}')

        except Exception as e:
            logger.error(f'Failed to send password reset email to {user.email}: {str(e)}')

    @staticmethod
    def send_detection_results_email(user, detection_result):
        """Send detection results via email"""
        try:
            subject = f'BioGuard AI - Detection Results for {detection_result.subject_type.title()}'

            context = {
                'user': user,
                'detection': detection_result,
                'results_url': f"{settings.FRONTEND_URL}/history",
                'year': timezone.now().year,
            }

            html_content = render_to_string('emails/detection_results.html', context)
            text_content = strip_tags(html_content)

            EmailService._send_email(
                subject=subject,
                message=text_content,
                recipient_list=[user.email],
                html_message=html_content,
            )

            logger.info(f'Detection results email sent to {user.email}')

        except Exception as e:
            logger.error(f'Failed to send detection results email to {user.email}: {str(e)}')

    @staticmethod
    def send_subscription_confirmation_email(user, subscription):
        """Send subscription confirmation email"""
        try:
            subject = 'BioGuard AI - Subscription Activated!'

            context = {
                'user': user,
                'subscription': subscription,
                'dashboard_url': f"{settings.FRONTEND_URL}/profile",
                'year': timezone.now().year,
            }

            html_content = render_to_string('emails/subscription_confirmation.html', context)
            text_content = strip_tags(html_content)

            EmailService._send_email(
                subject=subject,
                message=text_content,
                recipient_list=[user.email],
                html_message=html_content,
            )

            logger.info(f'Subscription confirmation email sent to {user.email}')

        except Exception as e:
            logger.error(f'Failed to send subscription confirmation email to {user.email}: {str(e)}')

    @staticmethod
    def send_trial_expiring_email(user, trial):
        """Send trial expiring notification"""
        try:
            subject = 'BioGuard AI - Your Trial is Expiring Soon'

            context = {
                'user': user,
                'trial': trial,
                'subscription_url': f"{settings.FRONTEND_URL}/profile",
                'year': timezone.now().year,
            }

            html_content = render_to_string('emails/trial_expiring.html', context)
            text_content = strip_tags(html_content)

            EmailService._send_email(
                subject=subject,
                message=text_content,
                recipient_list=[user.email],
                html_message=html_content,
            )

            logger.info(f'Trial expiring email sent to {user.email}')

        except Exception as e:
            logger.error(f'Failed to send trial expiring email to {user.email}: {str(e)}')

    @staticmethod
    def send_subscription_expiring_email(user, subscription):
        """Send subscription expiring notification"""
        try:
            subject = 'BioGuard AI - Your Subscription is Expiring Soon'

            context = {
                'user': user,
                'subscription': subscription,
                'renewal_url': f"{settings.FRONTEND_URL}/profile",
                'year': timezone.now().year,
            }

            html_content = render_to_string('emails/subscription_expiring.html', context)
            text_content = strip_tags(html_content)

            EmailService._send_email(
                subject=subject,
                message=text_content,
                recipient_list=[user.email],
                html_message=html_content,
            )

            logger.info(f'Subscription expiring email sent to {user.email}')

        except Exception as e:
            logger.error(f'Failed to send subscription expiring email to {user.email}: {str(e)}')

    @staticmethod
    def send_newsletter(subscribers, subject, content):
        """Send newsletter to subscribers"""
        try:
            # This would be used for marketing emails
            # For now, just log the action
            logger.info(f'Newsletter "{subject}" would be sent to {len(subscribers)} subscribers')

        except Exception as e:
            logger.error(f'Failed to send newsletter: {str(e)}')

    @staticmethod
    def _send_email(subject, message, recipient_list, html_message=None, from_email=None):
        """Internal method to send emails"""
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                to=recipient_list,
            )

            if html_message:
                email.attach_alternative(html_message, "text/html")

            email.send(fail_silently=False)

        except Exception as e:
            logger.error(f'Failed to send email: {str(e)}')
            raise