from mongoengine import Document, EmbeddedDocument, StringField, ListField, EmbeddedDocumentField, DateTimeField, \
    ReferenceField

from datetime import datetime, timezone

from models.user import User

class Section(EmbeddedDocument):
    title = StringField(required=True)
    paragraphs = ListField(StringField(), required=True)


class Biography(Document):
    title = StringField(required=True)
    sections = ListField(EmbeddedDocumentField(Section))
    updatedAt = DateTimeField(default=lambda: datetime.now(timezone.utc))
    user = ReferenceField(User, required=True)
    meta = {'collection': 'biography'}

    def to_json_dict(self):
        data = self.to_mongo().to_dict()
        data['_id'] = str(data['_id'])
        data.pop('user')
        return data
