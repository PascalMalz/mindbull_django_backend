from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.core.validators import MinLengthValidator 

class RegistrationToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Token for {self.user.username}"


from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
import uuid

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[MinLengthValidator(limit_value=5)]  # Set minimum length
    )
    password = models.CharField(max_length=128)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    def to_dict(self):
        return self.id
            

    @property
    def profile_picture_url(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        else:
            return settings.DEFAULT_PROFILE_PICTURE_URL  # Example default url
    objects = CustomUserManager()

    def __str__(self):
        return self.username
    

# ProfileInformation model (though it's likely to go in smartUserManagement)
from django.contrib.auth.models import User

class ProfileInformation(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(default="")
    profile_picture = models.CharField(max_length=255, default=None, null=True, blank=True)

    def __str__(self):
        return self.user.username

# Follow model (though it's likely to go in smartUserManagement)
class Follow(models.Model):
    follower = models.ForeignKey(CustomUser, related_name='follower', on_delete=models.CASCADE)
    following = models.ForeignKey(CustomUser, related_name='following', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)  # e.g., "accepted", "pending"

# Notification model (though it's likely to go in smartUserManagement)
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField()

# DirectMessage model (though it's likely to go in smartUserManagement)
class DirectMessage(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name='receiver', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



