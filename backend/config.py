import os
from datetime import timedelta
from urllib.parse import quote_plus


class Config:
    FRONTEND_URL = 'http://192.168.1.29'
    FRONTEND_PORT = 5173
    _mongo_user = os.getenv("MONGODB_USER")
    _mongo_password = quote_plus(os.getenv("MONGODB_PASSWORD"))
    _mongo_host = os.getenv("MONGODB_HOST")
    _mongo_port = os.getenv("MONGODB_PORT")
    _mongo_db = os.getenv("MONGODB_DATABASE")
    _mongo_to = os.getenv("MONGODB_TIMEOUT")
    MONGODB_HOST = (
        f"mongodb://{_mongo_user}:{_mongo_password}@"
        f"{_mongo_host}:{_mongo_port}/{_mongo_db}"
        f"?authSource={_mongo_db}&serverSelectionTimeoutMS={_mongo_to}"
    )
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
