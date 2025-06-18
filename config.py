import os
import configparser

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')

    db_type = os.getenv('DB_TYPE', config.get('database', 'db_type', fallback='sqlite')).lower()

    db_config = {
        'type': db_type,
    }

    if db_type == 'mysql':
        db_config.update({
            'host': os.getenv('MYSQL_HOST', config.get('database', 'mysql_host', fallback='localhost')),
            'port': os.getenv('MYSQL_PORT', config.get('database', 'mysql_port', fallback='3306')),
            'user': os.getenv('MYSQL_USER', config.get('database', 'mysql_user', fallback='root')),
            'password': os.getenv('MYSQL_PASSWORD', config.get('database', 'mysql_password', fallback='')),
            'db': os.getenv('MYSQL_DB', config.get('database', 'mysql_db', fallback='app_db')),
        })
    else:
        db_config.update({
            'path': os.getenv('SQLITE_PATH', config.get('database', 'sqlite_path', fallback='app.db')),
        })

    authentik_config = {
        'client_id': os.getenv("AUTHENTIK_CLIENT_ID", config.get("authentik", "AUTHENTIK_CLIENT_ID", fallback="CLIENT_ID")),
        'client_secret': os.getenv("AUTHENTIK_CLIENT_SECRET", config.get("authentik", "AUTHENTIK_CLIENT_SECRET", fallback="CLIENT_SECRET")),
        'authorize_url': os.getenv("AUTHENTIK_AUTHORIZE_URL", config.get("authentik", "AUTHENTIK_AUTHORIZE_URL", fallback="https://auth.example.com/application/o/authorize/")),
        'token_url': os.getenv("AUTHENTIK_TOKEN_URL", config.get("authentik", "AUTHENTIK_TOKEN_URL", fallback="https://auth.example.com/application/o/token/")),
        'metadata_url': os.getenv("AUTHENTIK_METADATA_URL", config.get("authentik", "AUTHENTIK_METADATA_URL", fallback="https://auth.example.com/application/o/application-slug/.well-known/openid-configuration")),
        'redirect_uri': os.getenv("AUTHENTIK_REDIRECT_URI", config.get("authentik", "AUTHENTIK_REDIRECT_URI", fallback="http://localhost:5000/auth/callback")),
        'scope': os.getenv("AUTHENTIK_SCOPE", config.get("authentik", "AUTHENTIK_SCOPE", fallback="openid email profile")),
    }

    redis_config = {
        'host': os.getenv('REDIS_HOST', 'localhost'),
        'port': int(os.getenv('REDIS_PORT', 6379))
    }

    return {
        'database': db_config,
        'authentik': authentik_config,
        'redis': redis_config
    }