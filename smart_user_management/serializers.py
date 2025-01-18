#Turn data into JSON format

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import RegistrationToken, CustomUser, Follow

from django.contrib.sites.shortcuts import get_current_site
import uuid

class CustomUserSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField() 
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'profile_picture_url', 'followers_count','following_count')
        read_only_fields = ('profile_picture',)  # Mark it as read-only to make it optional
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def get_followers_count(self, obj):
        # Count the number of entries in the Follow model where this user is being followed
        return Follow.objects.filter(following=obj).count()

    def get_following_count(self, obj):
        # Count the number of users this user is following
        return Follow.objects.filter(follower=obj).count()

    def create(self, validated_data):
        password = validated_data.pop('password')
        while True:
            # Generate a new UUID and check if it already exists in the database
            new_id = uuid.uuid4()
            if not CustomUser.objects.filter(id=new_id).exists():
                break  # Exit the loop if the generated UUID is unique
        validated_data['id'] = new_id  # Assign the unique UUID to the user
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            current_site = get_current_site(self.context['request'])
            profile_picture_url = f"https://{current_site.domain}{obj.profile_picture.url}"
            return profile_picture_url
        return None




class RegistrationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationToken
        fields = '__all__'


from rest_framework import serializers
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter

class SocialLoginSerializer(serializers.Serializer):
    provider = serializers.CharField(required=True, write_only=True)
    access_token = serializers.CharField(required=True, write_only=True)
    username = serializers.CharField(required=True, write_only=True)
class SocialLoginAdapter(OAuth2Adapter):
    def complete_login(self, request, app, token, response):
        client = self.get_client()
        access_token = token.token
        # Logic to retrieve user info and create/return user
        # Handle different providers (Google, Facebook, etc.)