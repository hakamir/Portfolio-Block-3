from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from mongoengine import connect

def init_db(app):
    connect(host=app.config['MONGODB_HOST'])
jwt = JWTManager()
limiter = Limiter(get_remote_address)
