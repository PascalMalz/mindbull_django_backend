#todo only allow login if email is confirmed
#todo allow FB and twitter authentication
#make username mandatory and not empty
#todo allow user not to be created when there was an exeption
from rest_framework.views import APIView
from rest_framework.response import Response
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView
from .serializers import SocialLoginSerializer, SocialLoginAdapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.instagram.views import InstagramOAuth2Adapter
from allauth.socialaccount.providers.amazon.views import AmazonOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from rest_framework import status
from rest_framework import generics, permissions, status
from django.http import JsonResponse
from .models import CustomUser 
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings
import logging
log = logging.getLogger(__name__)

class ResponseData:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)



from django.contrib.auth import get_user_model
User = get_user_model()

PROVIDER_ADAPTERS = {
    'google': GoogleOAuth2Adapter,
    'facebook': FacebookOAuth2Adapter,
    'github': GitHubOAuth2Adapter,
    'instagram': InstagramOAuth2Adapter,
    'amazon': AmazonOAuth2Adapter,
    # Add more providers as needed
}

#The SocialLoginAPI is getting the Social Auth data from the post and checks with the authprovider if this is a real user. If so create user if not created already and return refresh token

class SocialLoginAPI(APIView):
    serializer_class = SocialLoginSerializer
    permission_classes = (permissions.AllowAny,)
    def post(self, request, *args, **kwargs):
        log.debug(f"request.data: {request.data}")
        serializer = SocialLoginSerializer(data=request.data)
        #log.debug(f"serializer: {serializer}")
        serializer.is_valid(raise_exception=True)
        log.debug(f"test1")
        #log.debug(f"serializer.validated_data: {serializer.validated_data}")
        provider = serializer.validated_data['provider']
        id_token = request.data.get('id_token')
        access_token = serializer.validated_data['access_token']#
        log.debug(f"test2")
        username = serializer.validated_data['username']
        log.debug(f"test3")
        log.debug(f'username: {username}')

        #log.debug(f"Provider: {provider}")
        #log.debug(f"Access Token: {access_token}")

        adapter_class = PROVIDER_ADAPTERS.get(provider)
        if adapter_class:
            adapter = adapter_class(request)
            #log.debug(f"Adapter: {adapter}")
            #Receive e.g. client_id from settings:
            provider_settings = settings.SOCIALACCOUNT_PROVIDERS.get(provider, {}).get('APP', {})
            try:
                response_data = ResponseData(
                    id_token=id_token,
                    access_token=access_token,
                    client_id=provider_settings.get('client_id', '')
                )
                log.debug("response_data.client_id: %s", response_data.client_id)
                response = {
                    'id_token': id_token,
                }
                login = adapter.complete_login(request=request, app=response_data, token=access_token, response=response)
                log.debug("Login object: %s", login)
                log.debug("Type of login object: %s", type(login))


                if login:

                    email = login.user.email
                    print(f'try this {email}')
                    try:
                        user = User.objects.get(email=email)
                        log.debug('User doooooo exist :D')
                    except User.DoesNotExist:
                        log.debug('User does not exist :D')
                        # If user doesn't exist, create a new local user
                        user = CustomUser.objects.create_user(email=email,username=username, password=None)
                        if user:

                            # Send email confirmation
                            email_address = EmailAddress.objects.add_email(
                                self.request, user, user.email, confirm=True
                            )

                            email_confirmation = EmailConfirmation.create(email_address)

                            email_confirmation.sent = timezone.now()
                            email_confirmation.save()
                            log.debug('end email')
                    log.debug('neither?')
                    # Authenticate the user
                    log.debug(f'user_object: {user.email}')
                    log.debug(f'request=request, username=login.user.username{request, login.user.email}')

                    refresh = RefreshToken.for_user(user)
                    log.debug("Login seems successful")

                    return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
                else:
                    log.debug("Login failed")
                    return Response({'message': 'Login failed'}, status=status.HTTP_400_BAD_REQUEST)

            except OAuth2Error as e:
                log.exception(f"OAuth2Error: {e}")
                log.debug("Login error")
                return Response({'message': 'Invalid access token'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            log.debug("Invalid provider")
            return Response({'message': 'Invalid provider'}, status=status.HTTP_400_BAD_REQUEST)

class SocialLoginView(OAuth2LoginView):
    adapter_class = SocialLoginAdapter




from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import CustomUserSerializer
import logging
log = logging.getLogger(__name__)
from allauth.account.models import EmailConfirmation, EmailAddress
from django.utils import timezone
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken  # Import RefreshToken

class RegisterAPI(generics.CreateAPIView):
    serializer_class = CustomUserSerializer
    log.debug('start registering')
    #Override the mothod of CreateAPIView --> CreateModelMixin:
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        # Generate tokens for the user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Create a custom response with tokens
        response_data = {
            "message": "User registered successfully",
            "access_token": access_token,
            "refresh_token": str(refresh),
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        try:
            user = serializer.save(is_active=True)
            if user:

                # Send email confirmation
                email_address = EmailAddress.objects.add_email(
                    self.request, user, user.email, confirm=True
                )

                email_confirmation = EmailConfirmation.create(email_address)

                email_confirmation.sent = timezone.now()
                email_confirmation.save()
                log.debug('end email')
            
            return user  # Return the created user object
        except Exception as e:
            log.debug(f'User registration failed: {str(e)}')
            raise


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

class UserLoginAPI(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        log.debug(f'email, password: {email,password}')
        user = authenticate(email=email, password=password)
        log.debug(f'user: {user}')

        if user:
            # Generate tokens for the user
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response(
                {'message': 'User logged in successfully', 'login_success': True,
                'refresh': str(refresh), 'access': access_token},
                status=status.HTTP_200_OK
                )
        else:
            return Response(
                {'message': 'Invalid username or password', 'login_success': False},
                status=status.HTTP_401_UNAUTHORIZED
                )


#view to forward the email authentication (with email link) to a custom view

from django.shortcuts import render, redirect
from allauth.account.views import ConfirmEmailView
from django.urls import reverse_lazy

class CustomConfirmEmailView(ConfirmEmailView):
    template_name = 'account_confirm_email.html'  # Use your custom template

    def get(self, *args, **kwargs):
        # Call the parent class's get method to handle email confirmation
        response = super().get(*args, **kwargs)

        # Check if email confirmation was successful
        if self.object and self.object.email_address.verified:
            # Redirect to the new template
            return redirect(reverse_lazy('email_confirmed'))

        return response

from django.shortcuts import render

def email_confirmed(request):
    return render(request, 'email_confirmed.html')



#API to set the username (not in use)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import Http404

User = get_user_model()

class SetUsernameAPI(APIView):
    """
    API endpoint to set a username if it's not set for the user.
    """

    @login_required  # Ensure that the user is authenticated to access this endpoint
    def post(self, request, format=None):
        user = request.user

        if user.username:
            # If the user already has a username, return a message
            return Response({'message': 'Username already set'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # If the user doesn't have a username, set it based on the provided data
            username = request.data.get('username')

            if not username:
                return Response({'message': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the username is unique
            if User.objects.filter(username=username).exists():
                return Response({'message': 'Username is already taken'}, status=status.HTTP_400_BAD_REQUEST)

            # Set the username for the user
            user.username = username
            user.save()

            return Response({'message': 'Username set successfully'}, status=status.HTTP_200_OK)



#API to check if username exists
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import CustomUserSerializer
from .models import CustomUser
import logging

log = logging.getLogger(__name__)

class CheckUsernameAPI(generics.GenericAPIView):
    serializer_class = CustomUserSerializer

    def post(self, request):
        # Get the username from the request data
        username = request.data.get('username')

        # Check if a user with the same username already exists
        if CustomUser.objects.filter(username=username).exists():
            # User with the same username already exists, return a conflict response
            return Response(
                {
                    "message": "Username already exists",
                    "detail": "A user with this username already exists."
                },
                status=status.HTTP_409_CONFLICT
            )

        # If the username is not taken, return a success response
        return Response({"message": "Username is available"}, status=status.HTTP_200_OK)


#API to check if email exists
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import CustomUserSerializer
from .models import CustomUser
import logging

log = logging.getLogger(__name__)

class CheckEmailAPI(generics.GenericAPIView):
    serializer_class = CustomUserSerializer

    def post(self, request):
        # Get the email from the request data
        email = request.data.get('email')

        # Check if a user with the same email already exists
        if CustomUser.objects.filter(email=email).exists():
            # User with the same email already exists, return a conflict response
            return Response(
                {
                    "message": "Email already exists",
                    "detail": "A user with this email already exists."
                },
                status=status.HTTP_409_CONFLICT
            )

        # If the email is not taken, return a success response
        return Response({"message": "Email is available"}, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import CustomUserSerializer


class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        log.debug('HTTP_AUTHORIZATION:')
        log.debug(request.META.get('HTTP_AUTHORIZATION'))
        user = request.user
        serializer = CustomUserSerializer(request.user, context={'request': request})
        return Response(serializer.data)


import uuid
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def upload_profile_picture(request):
    if 'profile_picture' in request.FILES:
        user = request.user  # Grab the authenticated user
        
        # Generate a UUID for the filename
        image_uuid = str(uuid.uuid4())
        filename = f"{image_uuid}.jpg"  # You can choose the desired file extension

        user.profile_picture = request.FILES['profile_picture']
        user.profile_picture.name = filename  # Set the image filename to the generated UUID
        user.save()

        # Generate and return the image URL
        image_url = request.build_absolute_uri(user.profile_picture.url)
        return Response({"detail": "Profile picture updated successfully.", "image_url": image_url}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "No image file provided."}, status=status.HTTP_400_BAD_REQUEST)


def get_user_profile(request):
    user = request.user  # Assuming you have the authenticated user
    profile_info = ProfileInformation.objects.get(user=user)
    profile_data = {
        'bio': profile_info.bio,
        'profile_picture': profile_info.profile_picture,
        # Include other user-related data as needed
    }
    return JsonResponse(profile_data)
# views.py

#Retrieve ProfileInformation for same user (/) and others (/<int:user_id>)
# views.py
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import CustomUserSerializer

class ProfileInformationView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure user is logged in
    
    def get(self, request, user_id=None):
        if user_id is None:
            # No user_id in the URL, so use the currently logged-in user's ID
            user_id = request.user.id
        
        user = get_object_or_404(CustomUser, id=user_id)
        serializer = CustomUserSerializer(user, context={'request': request})
        return Response(serializer.data)



from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, Follow

class ToggleFollowUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        target_user = get_object_or_404(CustomUser, id=user_id)
        user = request.user

        if user == target_user:
            return JsonResponse({'error': 'You cannot follow yourself'}, status=400)

        follow_relationship, created = Follow.objects.get_or_create(follower=user, following=target_user)

        if not created:
            follow_relationship.delete()
            is_following = False
        else:
            is_following = True

        total_followers = Follow.objects.filter(following=target_user).count()
        return JsonResponse({'is_following': is_following, 'total_followers': total_followers})

# In your Django views.py file

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, Follow

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_follow_status(request, user_id):
    target_user = get_object_or_404(CustomUser, id=user_id)
    is_following = Follow.objects.filter(follower=request.user, following=target_user).exists()
    return JsonResponse({'is_following': is_following})

# Endpoint to follow / unfollow a user
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, Follow

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_follow_user(request, user_id):
    target_user = get_object_or_404(CustomUser, id=user_id)
    user = request.user

    if user == target_user:
        return JsonResponse({'error': 'You cannot follow yourself'}, status=400)

    follow_relationship, created = Follow.objects.get_or_create(follower=user, following=target_user)

    if not created:
        # Follow relationship exists, so we unfollow
        follow_relationship.delete()
        is_following = False
    else:
        # New follow relationship was created
        is_following = True

    # Count the current number of followers
    total_followers = Follow.objects.filter(following=target_user).count()

    return JsonResponse({'is_following': is_following, 'total_followers': total_followers})


# Filename: views.py
# Contains views to manage followers and following lists in a social application.

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, Follow
from .serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated

class GetFollowersList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, pk=user_id)
        followers = Follow.objects.filter(following=user)
        followers_data = CustomUserSerializer([follower.follower for follower in followers], many=True, context={'request': request})
        return Response(followers_data.data)

class GetIFollowList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, pk=user_id)
        following = Follow.objects.filter(follower=user)
        following_data = CustomUserSerializer([follow.following for follow in following], many=True, context={'request': request})
        return Response(following_data.data)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ProfileInformation

from rest_framework.parsers import JSONParser
#Not used right?
class UpdateProfileInformation(APIView):
    def post(self, request, user_id):
        try:
            profile_info = ProfileInformation.objects.get(user_id=user_id)
            data = JSONParser().parse(request)
            profile_info.bio = data.get('bio', profile_info.bio)
            if 'profile_picture' in request.FILES:
                profile_info.profile_picture = request.FILES['profile_picture']
            profile_info.save()
            # Return a success response as needed
            return Response({'message': 'Profile information updated successfully'})
        except ProfileInformation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser # Assuming your custom user model is named CustomUser
import json

@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def update_bio(request):
    try:
        user = request.user
        data = json.loads(request.body)
        bio = data.get('bio', '')

        # Update the user's bio
        user.bio = bio
        user.save()

        return JsonResponse({'message': 'Bio updated successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
import logging

log = logging.getLogger(__name__)

class TokenRefreshView(TokenViewBase):
    """
    Takes a refresh type JSON web token and returns an access type JSON web token if the refresh token is valid.
    """
    _serializer_class = api_settings.TOKEN_REFRESH_SERIALIZER

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh", "No refresh token provided")
        log.debug(f'Start of TokenRefreshView')
        log.debug(f'Provided refresh token: {refresh_token}')
        log.debug(f'request.user: {request.user}')
        # Check if the token is blacklisted
        try:
            decoded_token = RefreshToken(refresh_token)
            is_blacklisted = BlacklistedToken.objects.filter(token__jti=decoded_token['jti']).exists()
            if is_blacklisted:
                log.debug('Token is blacklisted')
                return Response({'error': 'This token has been blacklisted'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            log.debug(f'Error checking blacklist or decoding token: {e}')
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

        # Perform the token refresh
        response = super().post(request, *args, **kwargs)
        log.debug(f'Response.data: {response.data}')
        log.debug(f'Old refresh token: {refresh_token}')
        # Extract and log the refresh token from the response
        if 'refresh' in response.data:
            refresh_token_from_response = response.data['refresh']
            log.debug(f'New refresh token: {refresh_token_from_response}')
        else:
            log.debug('No refresh token found in the response')

        if response.status_code == 200:
            # Log the user making the request
            user = request.user if not request.user.is_anonymous else 'AnonymousUser'
            log.debug(f'User ID: {getattr(user, "id", "None")} - Username: {getattr(user, "username", "None")}')
        else:
            log.debug('Token refresh failed')

        log.debug('End of TokenRefreshView')
        return response

# views.py

from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class CheckTokenStatusAPIView(APIView):
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            untyped_token = UntypedToken(token)
            is_blacklisted = BlacklistedToken.objects.filter(token__jti=untyped_token['jti']).exists()

            if is_blacklisted:
                return Response({'status': 'Token is blacklisted'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'Token is valid and not blacklisted'}, status=status.HTTP_200_OK)
        except (TokenError, InvalidToken) as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)




