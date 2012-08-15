# Django settings for babytimeline project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('lilith', 'babytimeline@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'babytimeline'             # Or path to database file if using sqlite3.
DATABASE_USER = 'btl'             # Not used with sqlite3.
DATABASE_PASSWORD = 'b4t3l'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Germany/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de'

DEFAULT_LANGUAGE = 1

ugettext = lambda s: s

LANGUAGES = (
    ('de', ugettext('German')),
    ('en', ugettext('English')),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

EMAIL_HOST = 'mail.arcor.de'
EMAIL_HOST_USER = 'babytimeline'
EMAIL_HOST_PASSWORD = '--a0(so@v4d'
DEFAULT_FROM_EMAIL = 'babytimeline@gmail.com'

ACCOUNT_ACTIVATION_DAYS = 7

AUTHENTICATION_BACKENDS = (
    # this is the default backend, don't forget to include it!
    'django.contrib.auth.backends.ModelBackend',
    'socialregistration.auth.FacebookAuth', # Facebook
    'socialregistration.auth.OpenIDAuth', # OpenID
    )

FACEBOOK_API_KEY = "d8a78fa51bdef137ac9cf2903e65e5d1"
FACEBOOK_SECRET_KEY = "d84c06d21d981b8a9f1d9a3e751124b7"

LOGIN_URL = "/accounts/login"

LOGIN_REDIRECT_URL = "/"

ERROR_LOG_FILE='/home/www/babytimeline/logs/btl-exceptions'
ACTIONS_LOG_FILE='/home/www/babytimeline/logs/btl-actions'
USER_FILES='/home/www/babytimeline/app/babytimeline/user_files'

#### NOT USING DAJAX YET
# Will create http://yourdomain.com/dajaxice/...
#DAJAXICE_MEDIA_PREFIX = "dajaxice"

#DAJAXICE_FUNCTIONS = (
#    'timeline.ajax.timeline_details',
#    'timeline.ajax.show_photo_editor',
#)

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/home/www/babytimeline/app/babytimeline/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://babytimeline.de/site_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = 'http://babytimeline.de/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'g4^d_m$)yu4$cgw1$266e-0j#xpytl#h@5!t2mh--a0(so@v4d'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source','django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = ("django.core.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.request",
                               'multilingual.context_processors.multilingual',)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'babytimeline.logging_middleware.LoggingRequestMiddleware',
    'babytimeline.logging_middleware.LoggingExceptionMiddleware',
    'facebook.djangofb.FacebookMiddleware',
)

ROOT_URLCONF = 'babytimeline.urls'

TEMPLATE_DIRS = (
    "/home/www/babytimeline/app/babytimeline/templates"
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.flatpages',
    'babytimeline.timeline',
    'registration',
    'contact_form',
    'socialregistration',
    'south',
    'dbgettext'
)

try:
    from local_settings import *
except ImportError:
    pass



