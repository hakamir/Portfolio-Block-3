import os
from datetime import timedelta


class Config:
    FRONTEND_URL = 'http://192.168.1.29'
    FRONTEND_PORT = 5173
    MONGO_URI = f'mongodb://{os.getenv("MONGODB_HOST")}:{os.getenv("MONGODB_PORT")}/{os.getenv("MONGODB_DATABASE")}?serverSelectionTimeoutMS={os.getenv("MONGODB_TIMEOUT")}'
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
