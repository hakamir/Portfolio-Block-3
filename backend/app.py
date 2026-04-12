from flask import Flask
from flask_cors import CORS

from config import Config
from extensions import mongo, jwt, limiter
from routes import register_routes


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    limiter.init_app(app)
    mongo.init_app(app)
    jwt.init_app(app)

    register_routes(app)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
