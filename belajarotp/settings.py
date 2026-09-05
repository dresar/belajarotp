"""
Django settings for belajarotp project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production-1234567890')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
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

ROOT_URLCONF = 'belajarotp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'belajarotp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validators.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validators.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validators.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validators.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'id-id'

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#settings-default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================
# EMAIL CONFIGURATION - BELAJAR KONFIGURASI EMAIL
# ============================================

# OPSI 1: Console Email Backend (UNTUK TESTING/DEVELOPMENT)
# Email akan muncul di terminal/console, tidak dikirim ke email sebenarnya
# Cocok untuk development dan testing tanpa perlu setup SMTP
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# DEFAULT_FROM_EMAIL = 'noreply@belajarotp.com'

# OPSI 2: SMTP Email Backend - cPanel Email (AKTIF SEKARANG)
# Konfigurasi untuk email dari cPanel: eka@expedient609.com
# Konfigurasi diambil dari file .env
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'mail.expedient609.com')  # SMTP server dari cPanel
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '465'))  # Port 465 menggunakan SSL
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'True') == 'True'  # Port 465 menggunakan SSL, bukan TLS
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False') == 'True'  # Tidak menggunakan TLS untuk port 465
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'eka@expedient609.com')  # Email pengirim
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'INDAH&EKA123456789')  # Password email
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'eka@expedient609.com')  # Email default pengirim

# OPSI 2A: SMTP Email Backend - Gmail (Alternatif)
# Uncomment baris di bawah ini jika ingin menggunakan Gmail
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'  # Gmail SMTP
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'  # Email pengirim
# EMAIL_HOST_PASSWORD = 'your-app-password'  # App Password (bukan password biasa)
# DEFAULT_FROM_EMAIL = 'your-email@gmail.com'

# OPSI 3: SMTP untuk Email Lain (Yahoo, Outlook, dll)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.mail.yahoo.com'  # Yahoo SMTP
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@yahoo.com'
# EMAIL_HOST_PASSWORD = 'your-password'
# DEFAULT_FROM_EMAIL = 'your-email@yahoo.com'

# OPSI 4: SMTP untuk Mailtrap (Testing Email)
# Mailtrap adalah service untuk testing email tanpa mengirim email sebenarnya
# Daftar di https://mailtrap.io untuk mendapatkan credentials
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.mailtrap.io'
# EMAIL_PORT = 2525
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-mailtrap-username'
# EMAIL_HOST_PASSWORD = 'your-mailtrap-password'
# DEFAULT_FROM_EMAIL = 'noreply@belajarotp.com'

# ============================================
# CATATAN PENTING:
# ============================================
# 1. Untuk Gmail:
#    - Harus menggunakan App Password, bukan password biasa
#    - Cara buat App Password: Google Account > Security > 2-Step Verification > App Passwords
#    - Atau aktifkan "Less secure app access" (tidak disarankan)
#
# 2. Untuk Production:
#    - Gunakan SMTP Email Backend
#    - Jangan hardcode password di settings.py
#    - Gunakan environment variables atau Django Secret Key
#    - Contoh: EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
#
# 3. Untuk Testing:
#    - Gunakan Console Email Backend (sekarang aktif)
#    - Atau gunakan Mailtrap untuk testing yang lebih realistis
#
# 4. Email akan muncul di terminal jika menggunakan Console Backend
#    Cek output terminal tempat Anda menjalankan: python manage.py runserver

# Login URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

