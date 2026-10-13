"""Database choice from environment variables, so settings.py never needs hand edits.

DB_ENGINE=sqlite (default) uses db.sqlite3 next to manage.py.
DB_ENGINE=mysql uses DB_NAME, DB_USER, DB_PASSWORD, DB_HOST and DB_PORT (default 3306).
"""
from django.core.exceptions import ImproperlyConfigured

MYSQL_REQUIRED = ('DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST')


def database_settings(environ, base_dir, debug):
    engine = environ.get('DB_ENGINE', 'sqlite').strip().lower()

    if engine == 'sqlite':
        # Production (DEBUG off) must say which database it uses, so a console command
        # without the right variables cannot quietly create and migrate a SQLite file.
        if not debug and environ.get('ALLOW_SQLITE') != 'True':
            raise ImproperlyConfigured(
                'DB_ENGINE is not set while DEBUG is False. Set DB_ENGINE=mysql (with DB_NAME, '
                'DB_USER, DB_PASSWORD, DB_HOST) or ALLOW_SQLITE=True.'
            )
        return {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': base_dir / 'db.sqlite3',
            }
        }

    if engine == 'mysql':
        missing = [name for name in MYSQL_REQUIRED if not environ.get(name)]
        if missing:
            raise ImproperlyConfigured('DB_ENGINE=mysql needs: ' + ', '.join(missing))
        return {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': environ['DB_NAME'],
                'USER': environ['DB_USER'],
                'PASSWORD': environ['DB_PASSWORD'],
                'HOST': environ['DB_HOST'],
                'PORT': environ.get('DB_PORT', '3306'),
                'OPTIONS': {
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                },
            }
        }

    raise ImproperlyConfigured(f'Unknown DB_ENGINE {engine!r}. Use sqlite or mysql.')
