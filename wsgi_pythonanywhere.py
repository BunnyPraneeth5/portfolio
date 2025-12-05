import sys
import os

# Add your project directory to the sys.path
path = '/home/bunnypraneeth/portfolio'  # REPLACE your_username with your PythonAnywhere username
if path not in sys.path:
    sys.path.append(path)

# Set environment variable for Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
