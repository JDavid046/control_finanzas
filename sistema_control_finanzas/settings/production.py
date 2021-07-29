from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['misfinanzasapp.herokuapp.com']

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'd3m4vdcgu91aen',
        'USER':'bspaxremeencfx',
        'PASSWORD':'21a0b84ce8602b9e9ed68643cf7e43ef3b1f616bbb94f645c02c002ef98573f4',
        'HOST':'ec2-34-194-14-176.compute-1.amazonaws.com',
        'PORT':'5432',
    }
}

STATICFILES_DIRS = (BASE_DIR, 'sistema_control/static')