# flake8: noqa: F405

from JellyBot.settings import *  # noqa

# --- SECURITY

# Cross-site load in frame
X_FRAME_OPTIONS = 'DENY'

# For SecurityMiddleware
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# --- CSRF

CSRF_COOKIE_DOMAIN = 'raenonx.cc'
CSRF_TRUSTED_ORIGINS = ['bot.raenonx.cc']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader'
                ]),
            ],
        },
    },
]

# --- Static files

STATIC_ROOT = os.path.join(BASE_DIR, "static")

# --- Logging

LOGGING_ROOT = '../logs/Jelly-Bot/Application'
LOGGING_FILE_ROOT = os.path.join(LOGGING_ROOT, 'logs')
LOGGING_FILE_ERROR = os.path.join(LOGGING_FILE_ROOT, 'logs-severe.log')

# To see the log which level is < 30 (WARNING), `DEBUG` must set to 1.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
    },
}

sys.stdout = open(os.path.join(LOGGING_ROOT, 'app.log'), "w+")
sys.stderr = open(os.path.join(LOGGING_ROOT, 'app-error.log'), "w+")
