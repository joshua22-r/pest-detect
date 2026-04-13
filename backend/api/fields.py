import base64
import hashlib
from django.conf import settings
from django.db import models
from cryptography.fernet import Fernet, InvalidToken


def _get_encryption_key() -> bytes:
    key = getattr(settings, 'ENCRYPTION_KEY', None)
    if key:
        if isinstance(key, str):
            key = key.encode()
        try:
            base64.urlsafe_b64decode(key)
            return key
        except Exception:
            pass

    # Fallback derive a stable key from SECRET_KEY if ENCRYPTION_KEY is not set.
    secret_key = getattr(settings, 'SECRET_KEY', 'fallback-secret-key').encode()
    digest = hashlib.sha256(secret_key).digest()
    return base64.urlsafe_b64encode(digest)


def get_fernet() -> Fernet:
    return Fernet(_get_encryption_key())


class EncryptedCharField(models.CharField):
    description = "CharField that encrypts values at rest using Fernet"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 256)
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        if value is None:
            return value
        if value == '':
            return ''
        if isinstance(value, str) and value.startswith('gAAAA'):
            return value
        return self.encrypt(value)

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def to_python(self, value):
        if value is None or value == '':
            return value
        if isinstance(value, str):
            try:
                return self.decrypt(value)
            except InvalidToken:
                return value
        return value

    def encrypt(self, value):
        if value is None:
            return value
        if not isinstance(value, bytes):
            value = str(value).encode('utf-8')
        return get_fernet().encrypt(value).decode('utf-8')

    def decrypt(self, value):
        if value is None:
            return value
        if isinstance(value, str):
            try:
                return get_fernet().decrypt(value.encode('utf-8')).decode('utf-8')
            except InvalidToken:
                return value
        return value

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if kwargs.get('max_length', None) == 256:
            del kwargs['max_length']
        return name, path, args, kwargs
