from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['']

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

STATICFILES_DIRS = (os.path.join(BASE_DIR, '/sistema_control/static'),)
