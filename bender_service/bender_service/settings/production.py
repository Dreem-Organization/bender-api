# stl
import os

# 3p
from raven.transport.requests import RequestsHTTPTransport

# project
from .common import *

##########################
# SENTRY CONFIGURATION ##
##########################
RAVEN_CONFIG = {
    'dsn': os.environ.get('RAVEN_DSN'),
    'transport': RequestsHTTPTransport,
}
INSTALLED_APPS = INSTALLED_APPS + [
    'raven.contrib.django.raven_compat',
]

ACCESS_LOGS_CONFIG = {
    "MAX_BODY_SIZE": 5 * 1024,
    "DEBUG_REQUESTS": [
        {
            "request.path": "^/admin/",
            "request.headers.user_agent": "^Datadog",
        },
        {
            "request.path": "^/admin/",
            "request.headers.user_agent": "^Go-http-client",
        },
    ],
}

MIDDLEWARE.insert(0, 'django_access_logger.AccessLogsMiddleware')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # Don't disable Gunicorn's logger
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '(message) (asctime)',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'json': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.advanced_access_logs': {
            'level': 'INFO',
            'handlers': ['json'],
            'propagate': False,
        },
    },
}

# THIS SHOULD BE REMOVED SOMEDAY
SECRET_KEY = os.environ.get("DJ_SECRET_KEY")


SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'SCOPE': [
            'user',
            'repo',
            'read:org',
        ],
    }
}
