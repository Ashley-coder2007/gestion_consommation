# local_settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'socadel',
        'USER': 'postgres',
        'PASSWORD': '1111',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}