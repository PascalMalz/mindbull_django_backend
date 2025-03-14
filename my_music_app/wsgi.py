"""
WSGI config for my_music_app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_music_app.settings')
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
application = get_wsgi_application()
