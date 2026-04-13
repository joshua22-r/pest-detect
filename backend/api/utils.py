import re
import requests
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.html import strip_tags


def sanitize_string(value, max_length=None, allow_html=False):
    """
    Sanitize string input by removing potentially dangerous content
    """
    if not isinstance(value, str):
        return value

    # Remove null bytes
    value = value.replace('\x00', '')

    # Strip HTML tags if not allowed
    if not allow_html:
        value = strip_tags(value)

    # Remove potentially dangerous characters
    value = re.sub(r'[<>"\';()&]', '', value)

    # Trim whitespace
    value = value.strip()

    # Check length
    if max_length and len(value) > max_length:
        value = value[:max_length]

    return value


def validate_file_upload(file, allowed_types=None, max_size=None):
    """
    Validate uploaded file
    """
    if not file:
        raise ValidationError("No file provided")

    # Check file size
    if max_size and file.size > max_size:
        raise ValidationError(f"File size exceeds maximum allowed size of {max_size} bytes")

    # Check file type
    if allowed_types:
        content_type = file.content_type.lower()
        if content_type not in allowed_types:
            raise ValidationError(f"File type {content_type} not allowed. Allowed types: {', '.join(allowed_types)}")

        if content_type.startswith('image/'):
            try:
                from PIL import Image
                file.seek(0)
                Image.open(file).verify()
                file.seek(0)
            except Exception:
                raise ValidationError("Uploaded image is invalid or may be corrupted")

    # Check file name for dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
    if any(char in file.name for char in dangerous_chars):
        raise ValidationError("File name contains invalid characters")

    return True


def validate_email_domain(email):
    """
    Validate email address and domain to prevent disposable emails.
    """
    if not email:
        return False

    email = email.strip()
    try:
        EmailValidator()(email)
    except ValidationError:
        return False

    domain = email.split('@')[1].lower()

    # List of common disposable email domains
    disposable_domains = {
        '10minutemail.com', 'guerrillamail.com', 'mailinator.com',
        'temp-mail.org', 'throwaway.email', 'yopmail.com'
    }

    return domain not in disposable_domains


def generate_password_reset_token(user):
    """Generate a secure password reset token for a user."""
    token_generator = PasswordResetTokenGenerator()
    return token_generator.make_token(user)


def verify_password_reset_token(user, token):
    """Verify password reset token for the given user."""
    token_generator = PasswordResetTokenGenerator()
    return token_generator.check_token(user, token)


def encode_uid(user):
    return urlsafe_base64_encode(force_bytes(user.pk))


def decode_uid(uidb64):
    try:
        return force_str(urlsafe_base64_decode(uidb64))
    except Exception:
        return None


def get_google_user_info(id_token=None, access_token=None):
    """Verify Google token and return user info."""
    if id_token:
        url = 'https://oauth2.googleapis.com/tokeninfo'
        response = requests.get(url, params={'id_token': id_token}, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('aud') != settings.GOOGLE_CLIENT_ID:
            raise ValueError('Invalid Google token audience')
        return {
            'email': data.get('email'),
            'name': data.get('name') or data.get('email').split('@')[0],
            'provider_id': data.get('sub'),
        }

    if access_token:
        url = 'https://www.googleapis.com/oauth2/v3/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('aud') and data.get('aud') != settings.GOOGLE_CLIENT_ID:
            raise ValueError('Invalid Google access token audience')
        return {
            'email': data.get('email'),
            'name': data.get('name') or data.get('email').split('@')[0],
            'provider_id': data.get('sub'),
        }

    raise ValueError('Google token required')


def get_facebook_user_info(access_token):
    """Verify Facebook token and return user info."""
    app_access_token = f"{settings.FACEBOOK_APP_ID}|{settings.FACEBOOK_APP_SECRET}"
    debug_url = 'https://graph.facebook.com/debug_token'
    debug_params = {
        'input_token': access_token,
        'access_token': app_access_token,
    }
    response = requests.get(debug_url, params=debug_params, timeout=10)
    response.raise_for_status()
    debug_data = response.json().get('data', {})
    if not debug_data.get('is_valid'):
        raise ValueError('Invalid Facebook access token')

    user_url = 'https://graph.facebook.com/me'
    user_params = {
        'fields': 'id,name,email',
        'access_token': access_token,
    }
    user_resp = requests.get(user_url, params=user_params, timeout=10)
    user_resp.raise_for_status()
    data = user_resp.json()
    if 'email' not in data:
        raise ValueError('Facebook account does not provide email')
    return {
        'email': data.get('email'),
        'name': data.get('name') or data.get('email').split('@')[0],
        'provider_id': data.get('id'),
    }


def build_social_username(email, provider):
    base_username = email.split('@')[0].lower().replace('.', '_')
    return f"{base_username}_{provider}"
