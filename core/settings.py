# core/settings.py
from pathlib import Path
from decouple import Config, RepositoryEnv

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_PATH = BASE_DIR / 'static'
STATIC_ROOT = BASE_DIR / 'staticfiles'

if not STATIC_PATH.exists():
    STATIC_PATH.mkdir(exist_ok=True)

config = Config(RepositoryEnv(BASE_DIR / '.env'))

SECRET_KEY = config('SECRET_KEY', default='ndjango-nyumba-n-insecure-nyumba-n-anything-nyumba-n-works')
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = [
        "localhost",
        "127.0.0.1",
        ".ngrok-free.app",
        ".ngrok.app",
    ]

CSRF_TRUSTED_ORIGINS = [
        "https://*.ngrok-free.app",
        "https://*.ngrok.app",
    ]

INSTALLED_APPS = [
    #'django.contrib.gis',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party (KEEP THESE)
    'crispy_forms',
    'crispy_tailwind',
    'phonenumber_field',
    'widget_tweaks',

    # Your apps
    'accounts',
    'houses',
    'payments',
    'reviews',
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

ROOT_URLCONF = 'core.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# DATABASES = {
#     'default':{
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'housefinder',
#         'USER': 'root',
#         'PASSWORD': 'root',
#         'HOST': 'localhost',
#         'PORT': '3306'
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailOrUsernameModelBackend',  # Your custom backend FIRST
    'django.contrib.auth.backends.ModelBackend',      # Default backend second
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

MEDIA_PATH = BASE_DIR / 'media'
if not MEDIA_PATH.exists():
    MEDIA_PATH.mkdir(exist_ok=True)

MEDIA_HOUSE_PATH = BASE_DIR / 'media' / 'house'
if not MEDIA_HOUSE_PATH.exists():
    MEDIA_HOUSE_PATH.mkdir(exist_ok=True)


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CRISPY TAILWIND
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# SIMPLE LOGIN (NO ALLAUTH)
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

# GOOGLE reCAPTCHA KEYS
# RECAPTCHA_PUBLIC_KEY = '6LeqPwYsAAAAAKRQTwma1bziM9XypUJyTuGK3cVD'
# RECAPTCHA_PRIVATE_KEY = '6LeqPwYsAAAAADxnaPaQO7mgjJaMnfn3YgrzY1Y3'

RECAPTCHA_PRIVATE_KEY = config('RECAPTCHA_PRIVATE_KEY')
RECAPTCHA_PUBLIC_KEY = config('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_SITE_KEY = config('RECAPTCHA_SITE_KEY')
RECAPTCHA_SECRET_KEY = config('RECAPTCHA_SECRET_KEY')
RECAPTCHA_REQUIRED_SCORE = 0.85 

# RECAPTCHA_PUBLIC_KEY = config('RECAPTCHA_PUBLIC_KEY')
# RECAPTCHA_PRIVATE_KEY = config('RECAPTCHA_PUBLIC_KEY')
# ANOTHER_API_KEY = config('ANOTHER_API_KEY')

ANOTHER_API_KEY = 'AQ.Ab8RN6J-R-cDhJqWCWzqWPaPDh0XaCi4DtMfpW6Qw3NkqHYY8Q'

#GDAL_LIBRARY_PATH = r"C:\Program Files\GDAL\bin\gdal.dll"

FERNET_KEY = config('FERNET_KEY')

# SECURITY SETTINGS FOR PRODUCTION
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session and CSRF cookies secure
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SESSION_COOKING_AGE = 86400 # Two weeks in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# or get from environment variables
SUPPORT_EMAIL = config('SUPPORT_EMAIL', default='support@nyumbafinder.co.ke')


AMOUNT_TO_PAY_PER_HOUSE = config('AMOUNT_TO_PAY_PER_HOUSE', default='100')
AMOUNT_TO_PAY_YEAR = config('AMOUNT_TO_PAY_YEAR', default='800')


MPESA_CONSUMER_KEY = config("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = config("MPESA_CONSUMER_SECRET")
MPESA_BUSINESS_SHORTCODE = config("MPESA_BUSINESS_SHORTCODE")
MPESA_PASSKEY = config("MPESA_PASSKEY")
MPESA_CALLBACK_URL = config("MPESA_CALLBACK_URL")
MPESA_OAUTH_URL = config("MPESA_OAUTH_URL")
MPESA_STK_PUSH_URL = config("MPESA_STK_PUSH_URL")
