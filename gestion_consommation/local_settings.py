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
NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"
DEBUG = True