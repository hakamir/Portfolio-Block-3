import bcrypt
from mongoengine import Document, StringField


class User(Document):
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    role = StringField(required=True, choices=['artist', 'admin'], default='artist')
    meta = {'collection': 'users'}

    def verify_password(self, pwd: str) -> bool:
        return bcrypt.checkpw(pwd.encode('utf-8'), self.password.encode('utf-8'))

    def to_json_dict(self):
        data = self.to_mongo().to_dict()
        data['_id'] = str(data['_id'])
        return {
            'id': str(self.id),
            'email': self.email,
            'role': self.role,
        }