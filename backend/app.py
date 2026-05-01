from flask import Flask
from flask_cors import CORS

from config import load_settings
from extensions import jwt, limiter, init_db
from routes import register_routes

settings = load_settings()


def create_app():
    app = Flask(__name__)
    app.config["settings"] = settings
    app.config["JWT_SECRET_KEY"] = settings.jwt_secret_key
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = settings.jwt_access_token_expires_delta
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = settings.jwt_refresh_token_expires_delta
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
    app.config['JWT_COOKIE_SECURE'] = False  # True in prod (HTTPS)
    app.config['JWT_COOKIE_SAMESITE'] = 'Strict'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    CORS(app,
         supports_credentials=True,
         origins=[
             f"http://localhost:{settings.frontend_port}",
             f"{settings.frontend_url}:{settings.frontend_port}"
         ])
    limiter.init_app(app)
    init_db(settings)
    jwt.init_app(app)

    register_routes(app)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
