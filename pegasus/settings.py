"""
Django settings for pegasus project.

Generated by 'django-admin startproject' using Django 3.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os
import socket

# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ['DJANGO_PEGASUS_SECRET_KEY']

# Get all machines marked for development and turn on DEBUG for them
with open('./development_machines.txt', 'r') as dev_machine_file:
    dev_machines = dev_machine_file.read().split('\n')

dev_machines = [machine.strip() for machine in dev_machines]

DEBUG = socket.gethostname() in dev_machines

if not DEBUG:
    print("""
DEBUG is False. If you want to be in development mode,
make sure you add your device's hostname ({})
to development_machines.txt
    """.format(socket.gethostname()))

# Manually enable/disable debug for development
# DEBUG = False
# print('DEBUG = {}'.format(DEBUG))

# To keep POST data, we cannot append a trailing slash to post URLs
APPEND_SLASH = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'pegasus-pietelite.azurewebsites.net']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'rest_framework',
    'storages',
    'reels',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pegasus.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pegasus.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {

    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'pegasus',
        'USER': f"{os.environ['PEGASUS_SQL_USERNAME']}",
        'PASSWORD': f"{os.environ['PEGASUS_SQL_PASSWORD']}",
        'HOST': 'tcp:pegasus-pietelite.database.windows.net',
        'PORT': '1433',
        'AUTOCOMMIT': True,     # Set this true for now so we don't have to do extra commit work

        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'connection_timeout': 30,
        },
    },
    # 'sqlite': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


if DEBUG:
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
else:
    STATICFILES_STORAGE = 'reels.azure.blob.AzureStaticStorage'
    DEFAULT_FILE_STORAGE = 'reels.azure.blob.AzureMediaStorage'
    STATIC_URL = 'https://pieteliteblob.blob.core.windows.net/pegasus-static/'
    MEDIA_URL = 'https://pieteliteblob.blob.core.windows.net/pegasus-media/'
    STATIC_ROOT = STATIC_URL
    MEDIA_ROOT = MEDIA_URL
