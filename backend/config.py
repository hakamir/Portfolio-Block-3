import os
from datetime import timedelta


class Config:
    MONGO_URI = 'mongodb://localhost:27017/Portfolio?serverSelectionTimeoutMS=5000'
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
