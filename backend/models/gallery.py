from mongoengine import EmbeddedDocument, DateTimeField, IntField, StringField, Document, ListField, \
    EmbeddedDocumentField, ReferenceField

from models.user import User


class GalleryImage(EmbeddedDocument):
    src = StringField(required=True)
    title = StringField(required=True)
    location = StringField()
    date = DateTimeField()
    order = IntField()
    alt = StringField()


class Gallery(Document):
    slug = StringField(required=True, unique=True)
    title = StringField(required=True)
    order = IntField(required=True)
    images = ListField(EmbeddedDocumentField(GalleryImage))
    user = ReferenceField(User, required=True)
    meta = {'collection': 'galleries'}

    def to_json_dict(self):
        data = self.to_mongo().to_dict()
        data['_id'] = str(data['_id'])
        data.pop('user')
        for image in data['images']:
            image['date'] = image['date'].isoformat()
        return data
