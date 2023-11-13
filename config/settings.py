"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = os.getenv("SECRET_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")


# SECURITY WARNING: don't run with debug turned on in production!

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    "corsheaders",
    'django_filters',
    'character',
    'gamerecord',
    "storages",
    'articles',
    "django_apscheduler"
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # 가능한 최상단에 위치할 것
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases




# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_METHODS = [  # 허용할 옵션
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [ # 허용할 헤더
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-api-key"
]
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://sub.example.com",
    "http://localhost:8080",
    "http://127.0.0.1:9000",
    'https://port-0-eranca-gg-jvpb2alnb33u83.sel5.cloudtype.app',
    "https://www.rollthun.site"
]

CORS_ORIGIN_ALLOW_ALL = True


SITE_ID = 1

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 5,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',

    ],
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FileUploadParser",
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],


   
}


from datetime import timedelta

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8080',
    'http://ancacaca-env.eba-bdkhrdpq.ap-northeast-2.elasticbeanstalk.com',
    'https://ancacaca-env.eba-bdkhrdpq.ap-northeast-2.elasticbeanstalk.com',
    "https://eranca.kro.kr",
    "http://eranca.kro.kr",
    "https://www.eranca.kro.kr",
    "http://www.eranca.kro.kr",
    'https://port-0-eranca-gg-jvpb2alnb33u83.sel5.cloudtype.app',
    'https://www.rollthun.site'
]

CSRF_COOKIE_SAMESITE='Lax'
CSRF_COOKIE_HTTPONLY =True

SECURE_CROSS_ORIGIN_OPENER_POLICY=None
SESSION_COOKIE_SECURE=False


# MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

if os.getenv("DEBUG") == 'True':
    DEBUG = True
else:
    DEBUG = False

STATICFILES_LOCATION = 'static'
MEDIAFILES_LOCATION = 'media'

if DEBUG: 

    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")

    AWS_REGION = "ap-northeast-2"
    AWS_S3_CUSTOM_DOMAIN = "s3.%s.amazonaws.com/%s" % (
        AWS_REGION,
        AWS_STORAGE_BUCKET_NAME,
    )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DATABASE_NAME"),
            "USER": 'mechauk',
            "PASSWORD": os.getenv("DATABASE_PASSWORD"), # 데이터베이스 생성 시 작성한 패스워드
            "HOST": os.getenv("DATABASE_HOST"), # 코드 블럭 아래 이미지 참고하여 입력
            "PORT": "5432",
        }
    }
    MEDIA_URL = "http://%s/media/" % AWS_S3_CUSTOM_DOMAIN
    STATIC_URL = "http://%s/static/" % AWS_S3_CUSTOM_DOMAIN
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


else:   
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")

    AWS_REGION = "ap-northeast-2"
    AWS_S3_CUSTOM_DOMAIN = "s3.%s.amazonaws.com/%s" % (
        AWS_REGION,
        AWS_STORAGE_BUCKET_NAME,
    )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DATABASE_NAME"),
            "USER": 'mechauk',
            "PASSWORD": os.getenv("DATABASE_PASSWORD"), # 데이터베이스 생성 시 작성한 패스워드
            "HOST": os.getenv("DATABASE_HOST"), # 코드 블럭 아래 이미지 참고하여 입력
            "PORT": "5432",
        }
    }
    MEDIA_URL = "http://%s/media/" % AWS_S3_CUSTOM_DOMAIN
    STATIC_URL = "http://%s/static/" % AWS_S3_CUSTOM_DOMAIN
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    

APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"

APSCHEDULER_RUN_NOW_TIMEOUT = 9999999  # Seconds

SCHEDULER_DEFAULT = True # apps.py 참고

FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]


MAX_UPLOAD_SIZE = 15728640
DATA_UPLOAD_MAX_MEMORY_SIZE = 15728640
FILE_UPLOAD_MAX_MEMORY_SIZE = 15728640
DATA_UPLOAD_MAX_NUMBER_FIELDS = None


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "encoding": "utf-8",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / 'logs.log',
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
        },
        "gamerecord": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

import json
from collections import OrderedDict

file_data = OrderedDict()

file_data["type"] = "service_account"
file_data["project_id"] = "erancaocr"
file_data["private_key_id"] = os.getenv('GCP_JSON1')
file_data["private_key"] = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC6njt3Jbaan7yY\nbNgX+MXUzLt7qymGZPPHnPQN+7ycCR1w1oWR3NkZ/38orcE/1HcOs+mWL+5nLqv/\nCHu6hZ1wwqWSIJZz+Rh+oJ2hG9KyUdlLOKvbp80iD4Ncw8Nc4R9eXevWMRaZbunc\n2OS66EmJOeQP3qJAaJWfB+9vZ9K9HJTqdi9tqsqEsq3iGJigBmdcW/ppm5VUcAcd\nY7QGGcsUpWjJkMzVEoU2cJ7QlH8bwa0EGdlXXjf3UtX7xJTiRwp1rYDIrAcXk3AN\nvlQ3gsTg7clb8x0HF0oLWyOIW/8MtM6gJklkw/eWMHqBPUH7UzvrFUlRDAgbErNE\n1K5rWZS5AgMBAAECggEANB0q8wdrmnuAIbrHj84vhNEVjCAMzRSVBUnd16fUkGh1\nOcUWcNjRIdL5MiVvoYEWLFtuoDvLYjIk4uf+EWTtxgb9ULTb/w/xWK9Gxa5s5NI5\nkamGSKVwAhJ99yJOBLpzVZl52gtESd2w3jUNjup+Wp15hDsCaWUrX0lKgnxmW9vM\nqg4Vf89ZXzTH+rfL0D0eB0KOQVsxaRazYkkP/AwjfpJzqwhFXkvLqqZC1WPPMfVb\n9+fDO/m4dM0Ewl+/kcQcW9xktmvGWTIlUIWOebFC7AEuDfiu/+FLVJiKv6jKsoBe\n5Pk2oruAfIpyoW+EM0M3mq6iUzV8aEwirdEXepyvxwKBgQDn3bGK78NlyLp34AGF\njxEZnWKLONyPWlnemgO/2uf48VexTxz05FQ/hQyDUVMMs15IGI6l9p+1YSEz1rxN\nXH9nA866WT17JRHULfzAlpmEVFRf5RTA2TmjzxMY5jT6G+3A8BJOxU/fLExBSFRR\n5QmkOSGgMAwrrBFrzDd8KuEz+wKBgQDOCty//lmhXThgwyP/tqVqOFp35i1iZCQ1\nolEdpfxi6r6BRnz8a4NSFkXhNtvxPVGU5RzyJ+emSJih80jAIh0E3TXD19Z+gVuo\n1N5NCPbIq0JmNcP1UW0Ov28ZFkzzFnzwnbemcb0xdVsDea+ZdLiaQ2itMdDKQmPR\nRFD/+77H2wKBgBNqjSOFUGeFl5fSOk5k3Jm4hDgEWvPmLQBnBUlbm3FNRHqklVgs\nhqGLErEsbjfyDUMcS1W6gUU/DPi6UqpnxINr3jPcpTlasVODRlcaRWC/bxFYrZQ4\nnIsLHB5JqMYI8K/naqEOBNI7c2dEF0uEUnpeDmLLozlE/3B3eW38aT9hAoGAChuQ\nTr7ciMT48g5AotfD750KGx2olk4RVKw8zHaLFhMr+02I7h0cGRfMn8rAKWp3qRVA\nQUTh4U9oZXF43SwPPmDXtV7OP/B6naKrsR3CdX+pRzhV/5/Z+MI9Yf6tEbPFt0wV\naU3lGRsHtvjuO1n1gGPUK8Lo2jM9kFOIobYo2scCgYEAlXuQ938Qi4csG1S/UiMs\nQXPzqRLMCWpGw4NvEOigTTvSpktV3srsFhk6XczegU0nmT403n0IXswAcuvp/ebc\nhtbjNwabSA5XgpoIrmGT4OG2JSTdS1Xq5WbnhYRgPahwEmK33tdhSyv5YzxzNBuX\ncMtie+kz7GEQhu2U1LuO7ZE=\n-----END PRIVATE KEY-----\n"
file_data["client_email"] = "mechauk@erancaocr.iam.gserviceaccount.com"
file_data["client_id"] = os.getenv('GCP_JSON3')
file_data["auth_uri"] = "https://accounts.google.com/o/oauth2/auth"
file_data["token_uri"] = "https://oauth2.googleapis.com/token"
file_data["auth_provider_x509_cert_url"] = "https://www.googleapis.com/oauth2/v1/certs"
file_data["client_x509_cert_url"] = "https://www.googleapis.com/robot/v1/metadata/x509/mechauk%40erancaocr.iam.gserviceaccount.com"
file_data["universe_domain"] = "googleapis.com"

# Print JSON

with open('words.json', 'w') as make_file:
    json.dump(file_data, make_file, ensure_ascii=False, indent=2)

os.environ['GOOGLE_APPLICATION_CREDENTIALS']='words.json'

from google.cloud import vision

try:
    client = vision.ImageAnnotatorClient()
    print(client)
except:
    print('fail')