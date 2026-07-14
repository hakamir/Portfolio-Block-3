import uuid
import bcrypt
from mongoengine import Document, StringField, BooleanField, ValidationError


class User(Document):
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    role = StringField(required=True, choices=['artist', 'admin'], default='artist')
    is_active = BooleanField(default=False)
    storage_id = StringField(required=True, default=lambda: str(uuid.uuid4()))
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
            'is_active': self.is_active,
            'storage_id': self.storage_id,
        }

    def clean(self):
        if self.role == 'admin' and self.is_active:
            raise ValidationError('Admins accounts cannot be set as active artist')