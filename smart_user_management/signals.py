from django.apps import apps
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.conf import settings
import os

#This app is to configure the main settings dynamically and makes this app more modula
@receiver(post_migrate)
def your_app_post_migrate(sender, **kwargs):
    if sender.name == apps.get_app_config('smart_user_management').name:
        # Add your app's templates directory to TEMPLATES settings
        settings.TEMPLATES[0]['DIRS'].append(os.path.join(settings.BASE_DIR, 'smart_user_management', 'templates'))

        # Add ACCOUNT_EMAIL_CONFIRMATION settings
        settings.ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = 'email_confirmed'
        settings.ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = 'email_confirmed'

#To create a profile when a new user is created 
from django.db.models.signals import post_save
from django.dispatch import receiver
from smart_user_management.models import CustomUser
from .models import ProfileInformation

# Use CustomUser as the sender
@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        ProfileInformation.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_profile(sender, instance, **kwargs):
    instance.profileinformation.save()

