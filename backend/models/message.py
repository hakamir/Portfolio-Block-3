from mongoengine import Document, StringField, DateTimeField, BooleanField, ReferenceField
from datetime import datetime, timezone

from models.user import User


class Message(Document):
    user = ReferenceField(User, required=True)
    name = StringField(required=True, max_length=100)
    email = StringField(required=True)
    message = StringField(required=True)
    date = DateTimeField(default=datetime.now(timezone.utc))
    read = BooleanField(default=False)
    trashed = BooleanField(default=False)
    replied = BooleanField(default=False)
    replied_at = DateTimeField(default=None)
    meta = {'collection': 'messages'}

    def to_json_dict(self):
        data = self.to_mongo().to_dict()
        data['_id'] = str(data['_id'])
        data.pop('user')
        return data
