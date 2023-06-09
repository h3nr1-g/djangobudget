import os
from djangobudget.settings.common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGOBUDGET_DEBUG','off').lower() in ['on','enabled','1']

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGOBUDGET_SECRET_KEY','django-insecure-=#i*natu9b%=uqk&qp@p@-lxq%5mri@@#ac*n(5m0#daxm')

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE','djangobudget'),
        'USER': os.environ.get('MYSQL_USER','djangobudget'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD','djangobudget'),
        'HOST': os.environ.get('MYSQL_SERVER','localhost'),
        'PORT': int(os.environ.get('MYSQL_PORT','3306')),
        'OPTIONS': {
              'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        },
    }
}
