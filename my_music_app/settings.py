#todo activate flutter domain for cors headers in (prepared in this file)

"""
Django settings for my_music_app project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
#Adjust when change the site settings!!!!
#SITE_ID = 2
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

from pathlib import Path

#for rest test:
import os
from pathlib import Path

# Use UTF-8 encoding for files read/write
FILE_CHARSET = 'utf-8'

# Default charset to use for all `Content-Type` headers in HTTP responses
DEFAULT_CHARSET = 'utf-8'

#TEst######################################################################
#BASE_DIR = os.path.dirname(os.path.dirname(os.path(__file__)))


DEFAULT_PROFILE_PICTURE_URL = "/"


""" # Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Define the location where uploaded files will be stored on the local file system
# Make sure to use an absolute path
LOCAL_FILE_STORAGE_LOCATION = '/home/admin_0/django_sounds/sound_files'
# my_music_project/settings.py
MEDIA_ROOT = '/home/admin_0/django_sounds/sound_files'
# Optional: Set the URL prefix for serving files
# This is useful when serving files from Django development server
# If you are using a web server like Nginx or Apache to serve files, you can skip this.
#MEDIA_URL = '/media/' """

#new
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-xco3mt7*sr=d)^bsf9z9$q%-3ozk=xo44!ds$d4++d2-f=momj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['neurotune.de','www.neurotune.de','82.165.125.163'] #'82.165.125.163',


# Application definition

INSTALLED_APPS = [
    #custom admin view:
    #'jazzmin',
    'django.contrib.admin',
    #Auth is the basis for authentication and requred for most libraries!
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #own custom apps:
    'music_app.apps.MusicAppConfig',
    'smart_user_management.apps.SmartUserManagementConfig',
    #custom apps:
    'bootstrap5',
    'django.contrib.sites',
    'storages',
    'mongoengine',
    #'corsheaders',#A Django App that adds Cross-Origin Resource Sharing (CORS) headers to responses. This allows in-browser requests to your Django application from other origins.
    #Authentification through Django frontend
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.amazon',
    'allauth.socialaccount.providers.instagram',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.github',
    #Rest API Authentication:
    'rest_framework', #basis for simplejwt
    'rest_framework_simplejwt', #Advanced tokens e.g. encrypted token in rest
    'rest_framework_simplejwt.token_blacklist'# because of jwt refresh token rotation we need to blacklist the used one
]
#Maybe not as necessary anymore because of steaming api
DATA_UPLOAD_MAX_MEMORY_SIZE = 419430400  # Set to a larger value (400 MB in this example)
FILE_UPLOAD_MAX_MEMORY_SIZE = 419430400

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'smart_user_management.middleware.DebugMiddleware', # Added remoce in prod
    'django.middleware.locale.LocaleMiddleware', # Added
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #custom
    #'corsheaders.middleware.CorsMiddleware', # need to activate for PRODUCTION!!! 
]


#Deactivate in prodiction!!!:
# Allow all origins for simplicity (you might want to restrict this in production)
CORS_ALLOW_ALL_ORIGINS = True
#Activate in production!!!
CORS_ALLOWED_ORIGINS = [
    # Add the origin of your Flutter app here.
    "https://your-flutter-app-domain.com",
]
"""
#IP Restriction...
MIDDLEWARE += [
    'baipw.middleware.BasicAuthIPWhitelistMiddleware'
]

 BASIC_AUTH_WHITELISTED_IP_NETWORKS = [
    '93.218.51.213',
    '127.0.0.1',
    '0.0.0.0',#remove for security
] """
#...IP Restriction


ROOT_URLCONF = 'my_music_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            #os.path.join(BASE_DIR, 'rest_framework', 'templates'),  # Path to DRF templates
            #os.path.join(BASE_DIR, 'smart_user_management', 'templates'), #my custom templates
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',# `allauth` needs this from django.
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',


            ],
        },
    },
]

WSGI_APPLICATION = 'my_music_app.wsgi.application'

#SITE_ID=1
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

import mongoengine

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mindbull',
        'USER': 'passi',
        'PASSWORD': 'Arbeit-0',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
    'mongodb': {
        'ENGINE': 'djongo',
        'NAME': 'sound_mongo',  # Replace with your MongoDB database name
        'ENFORCE_SCHEMA': False,

    },
}
# Connect to MongoDB
mongoengine.connect('sound_mongo', host='localhost', port=27017)

# Import the necessary module
from django.db import connections


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

#custom-authent...
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'smart_user_management.authentication_backends.EmailBackend', # file path to customized authentication settings
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]
#...

#CustomUser Registration
AUTH_USER_MODEL = "smart_user_management.CustomUser" 

#custom-allauth...

#Page to land after login only for web app!
#LOGIN_REDIRECT_URL = '/'
#LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/' #Not for allauth valid
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = 'email_confirmed' #Used to redirect user after confirming email to this template (smart_user_management)
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = 'email_confirmed' #Used to redirect user after confirming email to this template (smart_user_management)



ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # Set email verification method
#ACCOUNT_AUTHENTICATION_METHOD = 'username_email'  # Allow login with username or email
ACCOUNT_EMAIL_REQUIRED = True  # Require email during registration
ACCOUNT_UNIQUE_EMAIL = True  # Ensure unique emails
ACCOUNT_USERNAME_REQUIRED = False  # Do not require a username


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/


#static files are handled different in production
STATIC_ROOT = os.path.join(BASE_DIR, 'static') # for production only
STATIC_URL = '/static/' #for development
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'smart_user_management/static')]


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Custom to debug requests and Knox Authentication Settings
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'  # <-- Added this is important for multipart
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
         'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}


# Default knox values if none are set 
from datetime import timedelta
from rest_framework.settings import api_settings
REST_KNOX = {
    'SECURE_HASH_ALGORITHM':'cryptography.hazmat.primitives.hashes.SHA512',
    'AUTH_TOKEN_CHARACTER_LENGTH': 64, # By default, it is set to 64 characters (this shouldn't need changing).
    'TOKEN_TTL': timedelta(minutes=45), # The default is 10 hours i.e., timedelta(hours=10)).
    'USER_SERIALIZER': 'knox.serializers.UserSerializer',
    'TOKEN_LIMIT_PER_USER': None, # By default, this option is disabled and set to None -- thus no limit.
    'AUTO_REFRESH': False, # This defines if the token expiry time is extended by TOKEN_TTL each time the token is used.
    'EXPIRY_DATETIME_FORMAT': api_settings.DATETIME_FORMAT,
}




EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.ionos.de'
EMAIL_PORT = 587  # Use the appropriate port provided by IONOS
EMAIL_USE_TLS = True  # Use TLS encryption
EMAIL_HOST_USER = 'noreply@audifull.de'
EMAIL_HOST_PASSWORD = 'dasistdasstarkepasswortdamitkeinerhackt'
DEFAULT_FROM_EMAIL = 'noreply@audifull.de'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        'APP': {
            'client_id': '748796111902-5dptap6iklf1ob2omivlqrjqvkoqv3ts.apps.googleusercontent.com',
            'secret': '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',
            'key': ''
        }
    }
}



""" SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            "client_id": "748796111902-5dptap6iklf1ob2omivlqrjqvkoqv3ts.apps.googleusercontent.com",
            "project_id": "sounds-396420",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["https://neurotune.de/accounts/google/login/callback/"],
            "javascript_origins": ["https://neurotune.de"],
            #"hd": "https://neurotune.de",
        }
    }
}  """
#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
#SECURE_SSL_REDIRECT=False
#SESSION_COOKIE_SECURE=False
#CSRF_COOKIE_SECURE=False


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(BASE_DIR) + "/logfile.log",
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
            'encoding': 'utf-8',  # Correct attribute for file encoding
        },

        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
        },
    }
}

SIMPLE_JWT = {
    #Token to access the API's
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    #Token to refresh the access token
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}