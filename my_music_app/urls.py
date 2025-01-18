"""
URL configuration for my_music_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# my_music_project/my_music_app/urls.py
from django.urls import path, include
from . import views
from django.contrib import admin
admin.autodiscover()



urlpatterns = [
    # Add any other project-level URLs here

    # Include the app's URLs
    path('music/', include('music_app.urls'), name = 'music'),
    path('', include('music_app.urls')),
    path('adminviewdefault/', admin.site.urls),
    path('accounts/', include('allauth.urls')), #security issue when activated (all account URL's open)
    path('sum/', include('smart_user_management.urls')),
]

#Accounts
""" 
account/signup.html: Template for the registration/signup form.
account/login.html: Template for the login form.
account/logout.html: Template for the logout view.
account/password_reset.html: Template for the password reset form.
account/password_reset_done.html: Template for the password reset done view.
account/password_reset_from_key.html: Template for the password reset from key form.
account/password_reset_from_key_done.html: Template for the password reset from key done view.
account/password_change.html: Template for the password change form.
account/set_password.html: Template for the set password form.
account/password_change_done.html: Template for the password change done view.
account/confirm_email.html: Template for confirming the email address after signup.
account/email/confirmation_signup_message.txt: Email template for email confirmation message.
account/email/confirmation_signup_subject.txt: Email template for email confirmation subject.
account/email/password_reset_key_message.txt: Email template for password reset key message.
account/email/password_reset_key_subject.txt: Email template for password reset key subject.
account/email/confirmation_signup_subject.txt: Email template for email confirmation subject.
account/email/password_reset_key_message.txt: Email template for password reset key message.
account/email/password_reset_key_subject.txt: Email template for password reset key subject.
account/email/confirmation_signup_message.txt: Email template for email confirmation message.
account/email/confirmation_signup_subject.txt: Email template for email confirmation subject.
account/email/password_reset_key_message.txt: Email template for password reset key message.
account/email/password_reset_key_subject.txt: Email template for password reset key subject.
account/email/confirmation_signup_message.txt: Email template for email confirmation message.
account/email/confirmation_signup_subject.txt: Email template for email confirmation subject.
account/email/password_reset_key_message.txt: Email template for password reset key message.
account/email/password_reset_key_subject.txt: Email template for password reset key subject. 
"""