import bcrypt
from mongoengine import Document, StringField


class User(Document):
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    meta = {'collection': 'users'}

    def verify_password(self, pwd: str) -> bool:
        return bcrypt.checkpw(pwd.encode('utf-8'), self.password.encode('utf-8'))