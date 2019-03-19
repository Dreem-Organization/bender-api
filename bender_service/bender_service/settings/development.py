from .common import *
import sys

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dev',
        'USER': 'dev',
        'PASSWORD': 'dev',
        'HOST': 'bender-database',
        'PORT': '5432',
    }
}

# Turn down email
# ACCOUNT_EMAIL_VERIFICATION = "none"
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# If test do not load demo
if len(sys.argv) > 1 and sys.argv[1] in ("test", "loaddata"):
    print("no demo")
    BENDER_LOAD_DEMO = False


SECRET_KEY = '***REMOVED***'
