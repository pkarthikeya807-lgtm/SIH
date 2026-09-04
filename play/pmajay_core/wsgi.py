"""
WSGI config for pmajay_core project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pmajay_core.settings')

application = get_wsgi_application()
