from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.urls import reverse
from django.contrib.sessions.models import Session
from .models import UserSession
from django.utils import timezone
from datetime import timedelta
import json


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to all responses
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'

        # Content Security Policy
        connect_src = [
            "'self'",
            "https://api.stripe.com",
            "https://*.stripe.com",
            "wss://api.stripe.com",
        ]

        if hasattr(settings, 'ALLOWED_HOSTS') and settings.ALLOWED_HOSTS:
            for host in settings.ALLOWED_HOSTS:
                if host and not host.startswith('localhost'):
                    connect_src.append(host)

        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https: blob:; "
            f"connect-src {' '.join(connect_src)}; "
        )

        csp += "; frame-ancestors 'none'; base-uri 'self'; form-action 'self';"

        response['Content-Security-Policy'] = csp

        return response


class SessionManagementMiddleware:
    """
    Middleware to manage user sessions, enforce concurrent limits, and track device info
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request
        if hasattr(request, 'user') and request.user.is_authenticated:
            self._track_session(request)

        response = self.get_response(request)

        # Process response
        return response

    def _track_session(self, request):
        """Track user session activity and enforce limits"""
        try:
            session_key = request.session.session_key
            if not session_key:
                return

            user = request.user
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            # Get or create user session record
            user_session, created = UserSession.objects.get_or_create(
                session_key=session_key,
                defaults={
                    'user': user,
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'device_info': self._get_device_info(request),
                }
            )

            if not created:
                # Update existing session
                user_session.ip_address = ip_address
                user_session.user_agent = user_agent
                user_session.device_info = self._get_device_info(request)
                user_session.update_activity()

            # Enforce concurrent session limits
            UserSession.enforce_concurrent_limits(user, session_key)

        except Exception as e:
            # Log error but don't break the request
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Session tracking error: {e}")

    def _get_client_ip(self, request):
        """Get the client's real IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _get_device_info(self, request):
        """Extract device and browser information"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        # Simple device detection - could be enhanced with a proper library
        device_info = {
            'user_agent': user_agent,
            'is_mobile': 'Mobile' in user_agent,
            'is_tablet': 'Tablet' in user_agent or 'iPad' in user_agent,
            'browser': self._detect_browser(user_agent),
            'os': self._detect_os(user_agent),
        }
        return device_info

    def _detect_browser(self, user_agent):
        """Simple browser detection"""
        if 'Chrome' in user_agent and 'Safari' in user_agent:
            return 'Chrome'
        elif 'Firefox' in user_agent:
            return 'Firefox'
        elif 'Safari' in user_agent and 'Chrome' not in user_agent:
            return 'Safari'
        elif 'Edge' in user_agent:
            return 'Edge'
        else:
            return 'Unknown'

    def _detect_os(self, user_agent):
        """Simple OS detection"""
        if 'Windows' in user_agent:
            return 'Windows'
        elif 'Mac OS X' in user_agent:
            return 'macOS'
        elif 'Linux' in user_agent:
            return 'Linux'
        elif 'Android' in user_agent:
            return 'Android'
        elif 'iOS' in user_agent:
            return 'iOS'
        else:
            return 'Unknown'