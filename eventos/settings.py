"""
Django settings for eventos project.

Generated by 'django-admin startproject' using Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-tj6+t!ij4r@d88=dzj(a4n8*e@wgb35s#i@+*mp61g__a4+^u4'

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
    # Apps do projeto
    'dashboard',
    'events',
    'people',
    'clients',
    'occurrences',
    'landing',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Custom middleware
    'eventos.middleware.LoginRequiredMiddleware',
]

ROOT_URLCONF = 'eventos.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'landing.context_processors.unread_messages_count',
                'people.context_processors.whatsapp_settings',
                'people.context_processors.pending_people_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'eventos.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'postgres': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'agenciaatitude',  # nome do banco de dados
        'USER': 'agenciaatitude',  # usuário do PostgreSQL
        'PASSWORD': '*Marien2012',  # senha do usuário
        'HOST': 'localhost',  # host do PostgreSQL
        'PORT': '',  # porta do PostgreSQL (vazio para padrão)
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Recife'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication settings
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'sistema_home'
LOGOUT_REDIRECT_URL = 'landing:home'

# Email settings (for password reset)
# For development, use console backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production, use SMTP
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.example.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@example.com'
# EMAIL_HOST_PASSWORD = 'your-password'
# DEFAULT_FROM_EMAIL = 'your-email@example.com'

# Configurações do WhatsApp
ENABLE_WHATSAPP_VALUE = os.getenv('ENABLE_WHATSAPP', '0')
print(f"ENABLE_WHATSAPP raw value: {ENABLE_WHATSAPP_VALUE}")
ENABLE_WHATSAPP = ENABLE_WHATSAPP_VALUE.lower() in ('true', 't', '1', 'yes', 'y')
print(f"ENABLE_WHATSAPP processed value: {ENABLE_WHATSAPP}")
WHATSAPP_API_URL = os.getenv('WHATSAPP_API_URL', 'https://webpicne.digisac.co/api/v1')
WHATSAPP_API_USER_ID = os.getenv('WHATSAPP_API_USER_ID', None)
WHATSAPP_API_TOKEN = os.getenv('WHATSAPP_API_TOKEN', None)

# Configurações do WhatsApp para notificações do gestor
MANAGER_WHATSAPP = os.getenv('MANAGER_WHATSAPP', None)
MANAGER_ID = os.getenv('MANAGER_ID', None)
NOTIFY_ON_REGISTRATION = os.getenv('NOTIFY_ON_REGISTRATION', '1').lower() in ('true', 't', '1', 'yes', 'y')
NOTIFY_ON_CONTACT = os.getenv('NOTIFY_ON_CONTACT', '1').lower() in ('true', 't', '1', 'yes', 'y')

# Configurações do Twilio para WhatsApp
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', None)
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', None)
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', None)
