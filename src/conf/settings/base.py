"""
Django settings for coin_exchange project.

Generated by 'django-admin startproject' using Django 2.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""
import datetime
import logging
import sys
from os.path import abspath, basename, dirname, join, normpath
from sentry_sdk.integrations.logging import LoggingIntegration

DJANGO_ROOT = dirname(dirname(abspath(__file__)))
SITE_ROOT = dirname(DJANGO_ROOT)
SITE_NAME = basename(DJANGO_ROOT)
sys.path.append(DJANGO_ROOT)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = dirname(DJANGO_ROOT)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*jd1cgw&5$oplh@zb7+d!!_^v#98ng3c5*qrz%skj(9hn7w4p%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEST = True

ALLOWED_HOSTS = []

# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'django_extensions',
    'rest_framework',
    'corsheaders',
    'django_filters',
    'tinymce',
    'rest_framework_swagger'
]

LOCAL_APPS = [
    'coin_base',
    'coin_crypto',
    'coin_system',
    'coin_exchange',
    'coin_user',
    'content'
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'conf.urls'

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

WSGI_APPLICATION = 'conf.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3' if 'test' in sys.argv else 'django.db.backends.mysql',
        'NAME': ':memory:' if 'test' in sys.argv else 'coin_exchange',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': 'SET character_set_connection=utf8mb4;'
                            'SET collation_connection=utf8mb4_unicode_ci;'
                            "SET NAMES 'utf8mb4';"
                            "SET CHARACTER SET utf8mb4;"
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

MEDIA_ROOT = normpath(join(SITE_ROOT, 'media'))
MEDIA_URL = '/media/'
STATIC_ROOT = normpath(join(SITE_ROOT, 'assets'))
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": ""
        },
        "KEY_PREFIX": "coin_exchange"
    }
}

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'common.http.custom_exception_handler',
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=60*60)
}

CORS_ORIGIN_ALLOW_ALL = True

TINYMCE_DEFAULT_CONFIG = {
    'width': '80%',
    'height': '300px'
}


# All of this is already happening by default!
sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)

EMAIL_FROM_NAME = 'Coinbowl'
EMAIL_FROM_ADDRESS = "info@coinbowl.com"

FRONTEND_HOST = 'http://staging.coinbowl.com'
EXCHANGE_API = 'http://localhost:8000/api/exchange'

COINBASE = {
    'API_KEY': 'SomeKey',
    'API_SECRET': 'SomeSecret',
    'ACCOUNTS': {
        'LTC': '',
        'ETH': '',
        'BTC': '',
        'BCH': '',
    }
}

BITSTAMP = {
    'URL': '',
    'CUSTOMER_ID': '',
    'API_KEY': '',
    'API_SECRET': '',
}

OPENEXCHANGERATES = {
    'URL': '',
    'API_KEY': ''
}

TWILIO = {
    'URL': '',
    'API_SID': 'something',
    'API_AUTH_TOKEN': 'something',
}
FROM_PHONE_NUMBER = ''

SLACK = {
    'TOKEN': '',
}
SLACK_CHANNEL = 'exchange-notification'

SENDGRID = {
    'API_KEY': ''
}

BITPAY_BTC = {
    'URL': 'https://insight.bitpay.com/api'
}

BITPAY_BCH = {
    'URL': 'https://bch-insight.bitpay.com/api'
}

ETHERSCAN = {
    'URL': 'http://api.etherscan.io/api',
    'API_KEY': ''
}
