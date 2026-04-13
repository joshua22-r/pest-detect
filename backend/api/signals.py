from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import PasswordHistory


@receiver(pre_save, sender=User)
def store_password_history(sender, instance, **kwargs):
    """Store the previous hashed password before updating a user record."""
    if not instance.pk:
        return

    try:
        existing_user = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return

    if existing_user.password and existing_user.password != instance.password:
        PasswordHistory.add_password_to_history(instance, existing_user.password)
