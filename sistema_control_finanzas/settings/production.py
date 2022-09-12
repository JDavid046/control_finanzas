from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['misfinanzasapp.pythonanywhere.com']

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'misfinanzasapp$default',
        'USER': 'misfinanzasapp',
        'PASSWORD': 'S1st3m4s',
        'HOST': 'misfinanzasapp.mysql.pythonanywhere-services.com',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

STATICFILES_DIRS = (os.path.join(BASE_DIR, '/sistema_control/static'),)