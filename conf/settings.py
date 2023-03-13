import os
from pathlib import Path
from environ import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# setup environment variables:
env = environ.Env()
# read the environment file — defaults to .evn file in conf so no parameters need to be passed here::
environ.Env.read_env()

# project secret key:
SECRET_KEY = env("SECRET_KEY")

# set up debug from environment
DEBUG = env("DEBUG")

# development mode is used in cases of static files — see documentation for more
DEVELOPMENT_MODE = env("DEVELOPMENT_MODE")

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'debug_toolbar',
    'django_json_widget',
    'django_htmx',
    'django_celery_beat',
    'user_configuration',
    'staff_schedule',
    'frontdesk',
    'tasks',
    'payments',
    'executive',
    'trainer',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    'django_htmx.middleware.HtmxMiddleware',
    'user_configuration.middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'user_configuration/templates/'),
            os.path.join(BASE_DIR, 'staff_schedule/templates/'),
            os.path.join(BASE_DIR, 'frontdesk/templates/'),
            os.path.join(BASE_DIR, 'executive/templates/'),
            os.path.join(BASE_DIR, "trainer/templates"),
            os.path.join(BASE_DIR, 'templates/'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'user_configuration.theme_context_processor.theme_renderer'
            ],
        },
    },
]

WSGI_APPLICATION = 'conf.wsgi.application'


DATABASES = {
    'default': env.db_url('DATABASE_URL')
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = [
   'django.contrib.auth.backends.ModelBackend',
   'user_configuration.authentication.EmailAuthBackend',
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/
if DEBUG:
    INTERNAL_IPS = [
        "127.0.0.1",
    ]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

APPEND_SLASH = True

LOGIN_URL = "user_configuration:staff-login"

AUTH_USER_MODEL = "user_configuration.CustomUser"

# CELERY DETAILS
CELERY_BROKER_URL = env('CELERY_BROKER_URL')

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

MEDIA_URL = "media/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'staff_schedule/static/'),
    os.path.join(BASE_DIR, 'user_configuration/static/'),
    os.path.join(BASE_DIR, 'static/')
]

MEDIA_ROOT = BASE_DIR / "uploads"

# STATIC_ROOT = "static"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
