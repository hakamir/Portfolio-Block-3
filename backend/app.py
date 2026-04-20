from flask import Flask
from flask_cors import CORS

from config import Config
from extensions import mongo, jwt, limiter
from routes import register_routes


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=[
        f"http://localhost:{app.config['FRONTEND_PORT']}",
        f"{app.config['FRONTEND_URL']}:{app.config['FRONTEND_PORT']}"
    ])
    limiter.init_app(app)
    mongo.init_app(app)
    jwt.init_app(app)

    register_routes(app)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
