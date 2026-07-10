from mongoengine import ReferenceField, Document, StringField, IntField, DateTimeField

from models.user import User


class OrphanGallery(Document):
    user = ReferenceField(User, required=True)
    gallery_slug = StringField(required=True)
    gallery_title = StringField(required=True)
    image_src = StringField(required=True)
    image_title = StringField(required=True)
    image_location = StringField()
    image_date = DateTimeField()
    image_alt = StringField()
    image_order = IntField(required=True)
    deleted_at = DateTimeField(required=True)
    meta = {'collection': 'orphan_galleries'}

    @property
    def relative_path(self):
        return f'{self.gallery_slug}/{self.image_src}'

    def to_json_dict(self):
        return {
            '_id': str(self.id),
            'gallery_title': self.gallery_title,
            'image_title': self.image_title,
            'image_location': self.image_location,
            'image_date': self.image_date.isoformat() if self.image_date else None,
            'image_alt': self.image_alt,
            'image_order': self.image_order,
            'src': self.relative_path,
            'deleted_at': self.deleted_at,
        }
