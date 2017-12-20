"""
WSGI config for ApiTest project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
import site
import sys
SITE_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(SITE_DIR)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ApiTest.settings")

application = get_wsgi_application()
