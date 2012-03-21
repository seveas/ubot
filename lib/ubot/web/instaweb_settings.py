# Basic settings for zero-configuration bots
import os
import ubot.web

datadir = os.path.expanduser(os.path.join('~', '.local', 'share', 'ubot'))
datadir = os.environ.get('UBOT_DATADIR', datadir)

DEBUG = TEMPLATE_DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(datadir, 'ubot_instaweb.db'),
    }
}
TIME_ZONE = 'Europe/Amsterdam'
SITE_ID = 1
USE_L10N = True
MEDIA_ROOT = os.path.join(os.path.dirname(ubot.web.__file__), 'media')
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/media/admin/'
SECRET_KEY = 'ub0tub0tub0tub0tub0tub0tub0tub0tub0tub0tub0tub0t'
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
ROOT_URLCONF = 'ubot.web.project_urls'
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.admindocs',

    # Ubot and its default helpers
    'ubot.web.control',
    'ubot.web.encyclopedia',
)
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
