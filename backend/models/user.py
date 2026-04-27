from mongoengine import Document, StringField


class User(Document):
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    meta = {'collection': 'users'}
