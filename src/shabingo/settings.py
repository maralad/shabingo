#!/usr/bin/env python
__author__ = 'Donagh Corcoran'
"""
Django settings for Shabingo project.
See Readme for details regarding shabingo_settings.cfg and ConfigParser
For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
import os
import ConfigParser

sha_config = ConfigParser.ConfigParser()
config_path =  os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),'shabingo_settings.cfg')      

#config_path=(os.path.join(os.path.abspath(os.path.dirname(__file__)),  'local_settings.cfg'))
sha_config.read(config_path) 
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


EMAIL_HOST = sha_config.get('EMAIL', 'EMAIL_HOST')

EMAIL_HOST_USER = sha_config.get('EMAIL', 'EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = sha_config.get('EMAIL', 'EMAIL_HOST_PASSWORD')
EMAIL_PORT = sha_config.get('EMAIL', 'EMAIL_PORT')
EMAIL_USE_TLS = sha_config.get('EMAIL', 'EMAIL_USE_TLS')

SECRET_KEY = sha_config.get('SECRET', 'SECRET_KEY')

DEBUG = False

SITE_ID = 1
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.formtools',
    'main',            
    'social.apps.django_app.default',
    'django.contrib.comments',
    'django.contrib.sites',
    'taggit',
    'favicon',
    'crispy_forms',
    'paypal.standard.ipn',
    'south',
)

TEMPLATE_CONTEXT_PROCESSORS = (
   'django.contrib.auth.context_processors.auth',
   'django.core.context_processors.debug',
   'django.core.context_processors.i18n',
   'django.core.context_processors.media',
   'django.core.context_processors.static',
   'django.core.context_processors.tz',
   'django.contrib.messages.context_processors.messages',
   'social.apps.django_app.context_processors.backends',
   'social.apps.django_app.context_processors.login_redirect',
)

AUTHENTICATION_BACKENDS = (
   'social.backends.facebook.FacebookOAuth2',
   'social.backends.email.EmailAuth',
   'social.backends.google.GoogleOAuth2',
   'social.backends.twitter.TwitterOAuth',
   'django.contrib.auth.backends.ModelBackend',
)
LOGIN_REDIRECT_URL = '/'
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = sha_config.get('DIRS', 'ROOT_URLCONF')
WSGI_APPLICATION = sha_config.get('DIRS', 'WSGI_APPLICATION')

SITE_ID = 1 


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': sha_config.get('DATABASES', 'NAME'),
        'USER': sha_config.get('DATABASES', 'USER'),
        'PASSWORD': sha_config.get('DATABASES', 'PASSWORD'),
    }
}


ALLOWED_HOSTS = ['shabingo.com','www.shabingo.com']

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SOCIAL_AUTH_FACEBOOK_KEY = sha_config.get('SOCIAL_AUTH', 'SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET =sha_config.get('SOCIAL_AUTH', 'SOCIAL_AUTH_FACEBOOK_SECRET')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_TWITTER_KEY = sha_config.get('SOCIAL_AUTH', 'SOCIAL_AUTH_TWITTER_KEY')
SOCIAL_AUTH_TWITTER_SECRET =sha_config.get('SOCIAL_AUTH', 'SOCIAL_AUTH_TWITTER_SECRET')
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = sha_config.get('SOCIAL_AUTH', 'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET =sha_config.get('SOCIAL_AUTH', 'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')

#AMAZON  SETTINGS...
AWS_URL=sha_config.get('AMAZON_SETTINGS', 'AWS_URL')
ACCESS_KEY_ID=sha_config.get('AMAZON_SETTINGS', 'ACCESS_KEY_ID')
SECRET_ACCESS_KEY=sha_config.get('AMAZON_SETTINGS', 'SECRET_ACCESS_KEY')



STATIC_URL = sha_config.get('STATIC_FILES', 'STATIC_URL')
CONTENT_TYPES = ['image', 'video']

MAX_UPLOAD_SIZE = 629916160
MAX_UPLOAD_1_SIZE = 99916160
MAX_UPLOAD_2_SIZE = 9916160

#paypal
PAYPAL_RECEIVER_EMAIL = sha_config.get('PAYPAL', 'PAYPAL_RECEIVER_EMAIL')
PAYPAL_TEST =False #sha_config.get('PAYPAL', 'PAYPAL_TEST')

#if DEBUG:
MEDIA_URL = sha_config.get('DIRS', 'MEDIA_URL')
STATIC_ROOT = sha_config.get('DIRS', 'STATIC_ROOT')
MEDIA_ROOT =  sha_config.get('DIRS', 'MEDIA_ROOT')
STATICFILES_DIRS =  (
    sha_config.get('DIRS', 'DIR_STATIC'),
 )
   
TEMPLATE_DIRS =(
     sha_config.get('DIRS', 'DIR_TEMPLATES'),
    
    )
    
TEMPLATE_LOADERS = ('django.template.loaders.filesystem.Loader',
 'django.template.loaders.app_directories.Loader')

TEST_SECRET_KEY=sha_config.get('STRIPE', 'TEST_SECRET_KEY')
TEST_PUBLISHABLE_KEY=sha_config.get('STRIPE', 'TEST_PUBLISHABLE_KEY')
LIVE_SECRET_KEY =sha_config.get('STRIPE', 'LIVE_SECRET_KEY')
TEST_SECRET_KEY =sha_config.get('STRIPE', 'TEST_SECRET_KEY')
DEV_CLIENT_ID =sha_config.get('STRIPE', 'DEV_CLIENT_ID')
PROD_CLIENT_ID=sha_config.get('STRIPE', 'PROD_CLIENT_ID')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename':  sha_config.get('LOGGING', 'FILE_NAME'),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'DEBUG',
        },
        'main': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}

WELCOME_EMAIL="""
Thanks for registering with Shabingo :).

Your Check List:

1. So you get paid directly by video viewers straight into your bank account you need to have a Stripe payments account. Follow a few very straight forward steps by clicking on the connect to stripe button in your My Shabingo section of the website. https://shabingo.com/accounts/loggedin2/


2. Before uploading your Videos you will need to prepare a seperate video preview clip for each video. So you will be uploading 2 clips at a time. This is where you can have some fun getting creative. The aim of the preview clip is to make it complelling enough for the viewer to really want to pay to see your full video clip or the "Full Shabingo".

3. All video Formats are supported.

4 .You will also be required to upload a poster image to go with the clip. .jpeg or .png are fine Maz size 50mb.

5. Have fun and get creative!

Thanks again for registering with us and we look forward to seeing your
creations live on Shabingo.com

Here is a quick link to start uploading:
http://shabingo.com/upload/

As soon as you upload a video best thing to do is go to
http://shabingo.com/videos/ and click on your video and share it on the
social networks. This is certain to increase your chance of making
money.

Please let us know what you would like to use Shabingo for and we will
be delighted to help you. Just reply to this email.

The very very best of regards,


The Shabingo team.

-- 

Shabingo.com

The webs marketplace for originally created Videos

-- 
https://shabingo.com
"""
