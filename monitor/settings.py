# -*- coding: utf-8 -*-
"""
Django settings for monitor project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=f2y0@0s_pufc+ia_bbf9vtv5++y3n$8080&5ve6=7&ne3tru!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'background',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'monitor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'monitor.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'monitor',
        'HOST': '',
        'PORT':3306,
        'USER':'root',
        'PASSWORD': 'build.ns',
         'OPTIONS':{'sql_mode':'STRICT_TRANS_TABLES'}
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    "%s/%s" %(BASE_DIR, "statics"),
)


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}


REDIS_CONN = {
    'HOST': 'localhost',
    'PORT': 6379,
    'PASSWD':''
}


STATUS_DATA_OPTIMIZATION = {
    'latest':[0,600],
    '10mins':[600,600], #4days
    '30mins':[1800,600],#14days
    '60mins':[3600,600], #25days
}

HOST_TIMEOUT_SECOND = 20




LOGGING_stamdard_format = '[%(asctime)s][task_id:%(name)s][%(filename)s:%(lineno)d] [%(levelname)s]- %(message)s'
LOGGING_simple_format = '[%(filename)s:%(lineno)d][%(levelname)s] %(message)s'
LOGGING_request_format = '[%(asctime)s][%(status_code)s][%(request)s] %(message)s'
REST_SESSION_LOGIN = False
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,# this fixes the problem
    'formatters': {
        'standard': {#详细
            'format': LOGGING_stamdard_format
        },
        'simple': {#简单
            'format': LOGGING_simple_format
        },
        'request': {#简单
            'format': LOGGING_request_format
        },
    },
    'filters': {},
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'console':{
            'level': 'INFO',
            'class': 'logging.StreamHandler',#打印到前台
            'formatter': 'simple'
        },
        'default': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR+'/logs/','all.log'), #或者直接写路径：'c:\logs\all.log',
            'maxBytes': 1024*1024*10, # 10 MB
            'backupCount': 5,
            'formatter':'standard',
        },
        'request': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR+'/logs/','request.log'), #或者直接写路径：'c:\logs\all.log',
            'maxBytes': 1024*1024*10, # 10 MB
            'backupCount': 5,
            'formatter':'request',
        },
        'db': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR+'/logs/','db.log'), #或者直接写路径：'c:\logs\all.log',
            'maxBytes': 1024*1024*10, # 10 MB
            'backupCount': 5,
            'formatter':'standard',
        },
        'scprits_handler': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR+'/logs/','scprits.log'), #或者直接写路径：'c:\logs\all.log',
            'maxBytes': 1024*1024*10, # 10 MB
            'backupCount': 5,
            'formatter':'standard',
        },
        'core': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR+'/logs/','core.log'), #或者直接写路径：'c:\logs\all.log',
            'maxBytes': 1024*1024*10, # 10 MB
            'backupCount': 5,
            'formatter':'standard',
        },
        'web_apps': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR+'/logs/','web_apps.log'), #或者直接写路径：'c:\logs\all.log',
            'maxBytes': 1024*1024*10, # 10 MB
            'backupCount': 5,
            'formatter':'standard',
        },
        'update_code': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR+'/logs/','update_code.log'), #或者直接写路径：'c:\logs\all.log',
            'maxBytes': 1024*1024*10, # 10 MB
            'backupCount': 5,
            'formatter':'standard',
        },
        'exec_command': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR+'/logs/','exec_command.log'), #或者直接写路径：'c:\logs\all.log',
            'maxBytes': 1024*1024*10, # 10 MB
            'backupCount': 5,
            'formatter':'standard',
        },
        'online_request': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR+'/logs/','online_request.log'), #或者直接写路径：'c:\logs\all.log',
            'maxBytes': 1024*1024*10, # 10 MB
            'backupCount': 5,
            'formatter':'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['default','console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['request','default'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'scripts': { # 脚本专用日志
            'handlers': ['scprits_handler','default','console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'web_apps': { # 脚本专用日志
            'handlers': ['web_apps','default'],
            'level': 'INFO',
            'propagate': False
        },
        'update_code': { # 脚本专用日志
            'handlers': ['update_code','default'],
            'level': 'INFO',
            'propagate': False
        },
        'exec_command': { # 脚本专用日志
            'handlers': ['exec_command','default'],
            'level': 'INFO',
            'propagate': False
        },
        'online_request': { # 脚本专用日志
            'handlers': ['online_request','default'],
            'level': 'INFO',
            'propagate': False
        },
        'core': { # 脚本专用日志
            'handlers': ['core','default','console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django.db.backends':{
            'handlers': ['db'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}