#todo restrict all the urls but email confirmation see todo.txt

from django.contrib.auth.views import LoginView
from . import views
from django.urls import path, include
from .views import RegisterAPI #,ConfirmRegistrationAPI
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf.urls.static import static
from django.conf import settings

from .views import CustomConfirmEmailView, email_confirmed
urlpatterns = [
    path('account/confirm-email/<str:key>/', CustomConfirmEmailView.as_view(), name='account_confirm_email'),
    path('email-confirmed/', email_confirmed, name='email_confirmed'),  # Define the URL for the new template
    path('auth/social/', views.SocialLoginAPI.as_view(), name='social-login'),
    path('auth/social/callback/', views.SocialLoginView, name='social-login-callback'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('api/login/', views.UserLoginAPI.as_view(), name='login'),#why here was register as a name?
    path('api/check-username/', views.CheckUsernameAPI.as_view(), name='check-username'),
    path('api/check-email/', views.CheckEmailAPI.as_view(), name='check-email'),
    path('api/user-profile/', views.ProfileInformationView.as_view(), name='current_user_profile'),
    path('api/user-profile/<uuid:user_id>/', views.ProfileInformationView.as_view(), name='user-profile'),
    path('api/user/<uuid:user_id>/follow/', views.ToggleFollowUser.as_view(), name='user-profile-follow'),
    path('api/user/<uuid:user_id>/check_follow/', views.check_follow_status, name='check-user-follow-status'),
    path('api/user/<uuid:user_id>/followers_list/', views.GetFollowersList.as_view(), name='get-followers-list'),
    path('api/user/<uuid:user_id>/i_follow_list/', views.GetIFollowList.as_view(), name='get-i-follow-list'),
    path('api/upload-profile-picture/', views.upload_profile_picture, name='upload-profile-picture'),
    path('api/update-bio/', views.update_bio, name='update_bio'),
    path('api/check_token_status/', views.CheckTokenStatusAPIView.as_view(), name='check_token_status'),
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
