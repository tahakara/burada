from flask import Flask
from flask import request, g
from sqlalchemy import inspect

from flask_cors import CORS

from utils.GlobalUtilities import str_to_bool
from utils.LogHandlerUtilities import RequestLogHandler

from logging import debug, info, warning, error, exception

from re import match
from os import getenv
from dotenv import load_dotenv
# region Env Load
load_dotenv()
debug(f"APP_NAME: {getenv('APP_NAME')}")
debug(f"APP_VERSION: {getenv('APP_VERSION')}")
debug(f"APP_DESCRIPTION: {getenv('APP_DESCRIPTION')}")
debug(f"APP_SECRET_KEY: {getenv('APP_SECRET_KEY')}")
debug(f"APP_HOST: {getenv('APP_HOST')}")
debug(f"APP_PORT: {getenv('APP_PORT')}")
debug(f"APP_DEBUG: {getenv('APP_DEBUG')}")
debug(f"APP_LOG_LEVEL: {getenv('APP_LOG_LEVEL')}")
debug(f"DB_HOST: {getenv('DB_HOST')}")
debug(f"DB_PORT: {getenv('DB_PORT')}")
debug(f"DB_USER: {getenv('DB_USER')}")
debug(f"DB_PASSWORD: {getenv('DB_PASSWORD')}")
debug(f"DB_NAME: {getenv('DB_NAME')}")
debug(f"DB_CHARSET: {getenv('DB_CHARSET')}")
debug(f"DB_COLLATION: {getenv('DB_COLLATION')}")
debug(f"DB_DRIVER: {getenv('DB_DRIVER')}")
debug(f"REDIS_HOST: {getenv('REDIS_HOST')}")
debug(f"REDIS_PORT: {getenv('REDIS_PORT')}")
debug(f"REDIS_USER: {getenv('REDIS_USER')}")
debug(f"REDIS_PASSWORD: {getenv('REDIS_PASSWORD')}")
debug(f"REDIS_DB: {getenv('REDIS_DB')}")
debug(f"JWT_SECRET_KEY: {getenv('JWT_SECRET_KEY')}")
debug(f"JWT_ALGORITHM: {getenv('JWT_ALGORITHM')}")
debug(f"JWT_EXPIRATION_TIME: {getenv('JWT_EXPIRATION_TIME')}")
debug(f"JWT_ISSUER: {getenv('JWT_ISSUER')}")
debug(f"JWT_REFRESH_TOKEN_EXPIRATION_TIME: {getenv('JWT_REFRESH_TOKEN_EXPIRATION_TIME')}")

APP_NAME = str(getenv('APP_NAME', 'Dust'))
APP_VERSION = str(getenv('APP_VERSION', '1.0.0'))
APP_DESCRIPTION = str(getenv('APP_DESCRIPTION', 'Burada App'))
APP_SECRET_KEY = str(getenv('APP_SECRET_KEY', 'Bi de Seviyom dedi Sana yanıyom dedi. İnan ölüyom dedi vah, vah, vahİş verip tüydü ortada koydu Aşkıma kıydı vah, vah, vah'))
APP_HOST = str(getenv('APP_HOST', '127.0.0.1'))
APP_PORT = int(getenv('APP_PORT', '5261')) if match(r'^\d+$', getenv('APP_PORT', '5261')) else 5261
APP_DEBUG = str_to_bool(getenv('APP_DEBUG', 'false'))
APP_LOG_LEVEL = str(getenv('APP_LOG_LEVEL', 'debug'))

DB_HOST = str(getenv('DB_HOST', '127.0.0.1'))
DB_PORT = int(getenv('DB_PORT', '3306')) if match(r'^\d+$', getenv('DB_PORT', '3306')) else 3306
DB_USER = str(getenv('DB_USER', 'root'))
DB_PASSWORD = str(getenv('DB_PASSWORD', '1234'))
DB_NAME = str(getenv('DB_NAME', 'burada'))
DB_CHARSET = str(getenv('DB_CHARSET', 'utf8mb4'))
DB_COLLATION = str(getenv('DB_COLLATION', 'utf8mb4_general_ci'))
DB_DRIVER = str(getenv('DB_DRIVER', 'mysql'))

REDIS_HOST = str(getenv('REDIS_HOST', '127.0.0.1'))
REDIS_PORT = int(getenv('REDIS_PORT', '6379')) if match(r'^\d+$', getenv('REDIS_PORT', '6379')) else 6379
REDIS_USER = str(getenv('REDIS_USER', 'default'))
REDIS_PASSWORD = str(getenv('REDIS_PASSWORD', '1234'))
REDIS_DB = int(getenv('REDIS_DB', '0')) if match(r'^\d+$', getenv('REDIS_DB', '0')) else 0

JWT_SECRET_KEY = str(getenv('JWT_SECRET_KEY', 'SomeSecretKey'))
JWT_ALGORITHM = str(getenv('JWT_ALGORITHM', 'HS256'))
JWT_EXPIRATION_TIME = int(getenv('JWT_EXPIRATION_TIME', '3600')) if match(r'^\d+$', getenv('JWT_EXPIRATION_TIME', '3600')) else 3600
JWT_ISSUER = str(getenv('JWT_ISSUER', 'https://burada.example.com'))
JWT_REFRESH_TOKEN_EXPIRATION_TIME = int(getenv('JWT_REFRESH_TOKEN_EXPIRATION_TIME', '172800')) if match(r'^\d+$', getenv('JWT_REFRESH_TOKEN_EXPIRATION_TIME', '172800')) else 172800
DB_URL = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
# DB_URL = f'mysql+pymysql://root:1234@mysql:3306/burada'
debug(f"DB_URL: {DB_URL}")

# endregion

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = str(getenv('APP_SECRET_KEY', 'You were the Chosen One! It was said that you would destroy the Sith, not join them! Bring balance to the Force, not leave it in darkness! You were my brother, Anakin! I loved you!'))
    app.config['TEMPLATES_AUTO_RELOAD'] = True


    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    app.url_map.strict_slashes = False

    from middleware.app_middleware import middleware_bp


    from routes.bots import bots_bp
    from routes.errors import errors_bp
    from routes.dust import dust_bp
    from routes.burada import burada_bp

    from routes.link import link_bp

    from routes.auth import auth_bp
    from routes.dashboard import dash_bp
    from routes.profile import profile_bp
    app.register_blueprint(middleware_bp)

    app.register_blueprint(errors_bp)
    app.register_blueprint(bots_bp)
    app.register_blueprint(dust_bp)
    app.register_blueprint(burada_bp, url_prefix='/burada')

    app.register_blueprint(link_bp, url_prefix='/l')

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dash_bp, url_prefix='/dashboard')
    app.register_blueprint(profile_bp, url_prefix='/profile')


    return app

app = create_app()

CORS(app, supports_credentials=True)
# CORS(app, resources={r"/*": {"origins": "*"}})


# region DB Config
from modal import db

db.init_app(app)
with app.app_context():
    inspector = inspect(db.engine)
    if not inspector.get_table_names():
        db.create_all()

# endregion

if __name__ == '__main__':
    from functools import partial
    if not APP_DEBUG:
        app.config['ENV'] = 'development'
        app.config['DEBUG'] = True
    app.run(debug=APP_DEBUG, host=APP_HOST, port=APP_PORT, request_handler=partial(RequestLogHandler))