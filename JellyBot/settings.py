import os
import sys

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

###############################################################################################
# https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/                           #
# Check DEBUG, PRODUCTION keys is in a correct state                                          #
# Run "In Production" config to ensure runnable                                               #
# Run "py manage.py check --deploy" config to ensure no compiling bugs                        #
#   Disregard: security.W004, security.W008, security.W012, security.W016                     #
# Run "py manage.py makemessages -a" to create translation files (compilemessages for *.mo)   #
# Run tests                                                                                   #
###############################################################################################

# --- Main

SECRET_KEY = os.environ.get('SECRET_KEY')
if SECRET_KEY is None:
    print('Django SECRET_KEY undefined.')
    sys.exit(1)

DEBUG = bool(int(os.environ.get('DEBUG', 0)))

PRODUCTION = bool(int(os.environ.get('PRODUCTION', 1)))

# --- Application definition

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

ALLOWED_HOSTS = [
    # Local IP addresses
    'testserver',
    'localhost',
    '127.0.0.1',
    '192.168.50.33',
    # URL Domain of the bot
    'bot.raenonx.cc',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sanitizer',
    'JellyBot'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'JellyBot.components.middleware.RootUserIDInsertMiddleware',
    'JellyBot.components.middleware.APIStatisticsCollector',
    'JellyBot.components.middleware.TimezoneActivator',
    'JellyBot.components.middleware.TranslationActivator'
]

ROOT_URLCONF = 'JellyBot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'JellyBot.wsgi.application'

# --- Database
# --- https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# --- Password validation
# --- https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

# --- Internationalization
# --- https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-tw'

LANGUAGES = (
    ('en-us', _('English')),
    ('zh-tw', _('Traditional Chinese')),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# --- Static files (CSS, JavaScript, Images)
# --- https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

# --- Authorization

LOGIN_URL = reverse_lazy("account.login")

# --- On-Error handling

ADMINS = [('RaenonX JELLYCAT', os.environ.get("EMAIL_ACCOUNT"))]

# --- Email

if os.environ.get("EMAIL_ACCOUNT") is None:
    sys.exit("EMAIL_ACCOUNT not set in environment variable.")
if os.environ.get("EMAIL_PASSWORD") is None:
    sys.exit("EMAIL_PASSWORD not set in environment variable.")
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("EMAIL_ACCOUNT")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# --- Sanitizer

SANITIZER_ALLOWED_TAGS = ['div', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span',
                          'p', 'pre', 'code', 'br', 'img', 'ul', 'li']
SANITIZER_ALLOWED_ATTRIBUTES = ['class', 'id', 'role', 'data-toggle', 'href', 'aria-labelledby', 'src']
SANITIZER_ALLOWED_STYLES = []
