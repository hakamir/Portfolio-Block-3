from mongoengine import Document, StringField, DateTimeField, BooleanField
from datetime import datetime, timezone


class Message(Document):
    name = StringField(required=True, max_length=100)
    email = StringField(required=True)
    message = StringField(required=True)
    date = DateTimeField(default=datetime.now(timezone.utc))
    read = BooleanField(default=False)
    trashed = BooleanField(default=False)
    meta = {'collection': 'messages'}

    def to_json_dict(self):
        data = self.to_mongo().to_dict()
        data['_id'] = str(data['_id'])
        return data
