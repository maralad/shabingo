# README #
# This is the entire code that powers a fully functional video platform.. https://shabingo.com#
* The only thing you will need to add to it to get it working is your setttings. 
* The shabingo_settings.cfg where settings.py gets all the passwords and secure information is stored in a private repo.
* Below is what shabingo_settings.cfg keys are. Enter your own values for your server, database, stripe ids etc. 
# Fill out the .cfg and save it somewhere on your server like /etc or somewhere secure where apache cannot read#
* Then just point the config parser to its location.
*When running locally point the config parser to the location of the local shabingo_settings.cfg file and vice versa for in production.
And that's all you have to do to make it work localy and in production.

[EMAIL]
EMAIL_HOST = xxx

EMAIL_HOST_USER = xxx

EMAIL_HOST_PASSWORD = xxx

EMAIL_PORT = xxx

EMAIL_USE_TLS = xxx

[SECRET]
SECRET_KEY = xxx



[DATABASES]
NAME = xxx
USER = xxx
PASSWORD = xxx

[SOCIAL_AUTH]
SOCIAL_AUTH_FACEBOOK_KEY = xxx
SOCIAL_AUTH_FACEBOOK_SECRET = xxx
SOCIAL_AUTH_TWITTER_KEY = xxx
SOCIAL_AUTH_TWITTER_SECRET = xxx
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = xxx #Not currently implmented
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = xxx #Not currently implmented

[AMAZON_SETTINGS]
AWS_URL = xxx 
ACCESS_KEY_ID = xxx
SECRET_ACCESS_KEY = xxx

[STATIC_FILES]
STATIC_URL = /static/


[PAYPAL]
PAYPAL_RECEIVER_EMAIL = xxx
PAYPAL_TEST = False

[DIRS]
MEDIA_URL = /static/media/
STATIC_ROOT = xxx/shabingo_static/
MEDIA_ROOT =  xxx/shabingo_static/media/
DIR_STATIC=   xxx/shabingo_static/
DIR_TEMPLATES= xxx/shabingo_static/templates/
ROOT_URLCONF = shabingo.urls
WSGI_APPLICATION = shabingo.wsgi.application

[LOGGING]
FILE_NAME = xxx/Shabingo.log

[STRIPE]
TEST_SECRET_KEY =sk_test_xxx
TEST_PUBLISHABLE_KEY = pk_test_xxx
LIVE_SECRET_KEY = sk_live_xxx
TEST_SECRET_KEY =pk_live_xxx
DEV_CLIENT_ID =ca_xxx
PROD_CLIENT_ID=ca_xxx
