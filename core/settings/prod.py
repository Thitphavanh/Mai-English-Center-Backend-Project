import os
from .base import *

# In production, use environment variables to load secrets
SECRET_KEY = os.environ.get('SECRET_KEY', 'replace-me-in-production')

DEBUG = False

# Example allowed hosts for production
ALLOWED_HOSTS = ['yourdomain.com', 'api.yourdomain.com']

# Production Database (example configuration using PostgreSQL, you may need to add dj-database-url / psycopg2 to requirements)
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": "mai_english_db",
#         "USER": "mai_user",
#         "PASSWORD": "yourpassword",
#         "HOST": "localhost",
#         "PORT": "5432",
#     }
# }

# Static files handling in production
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
