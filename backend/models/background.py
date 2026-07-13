from mongoengine import EmbeddedDocument, StringField, Document, ReferenceField, EmbeddedDocumentField

from models.user import User


class BackgroundImage(EmbeddedDocument):
    sm = StringField(required=True)
    md = StringField(required=True)
    lg = StringField(required=True)


class Background(Document):
    user = ReferenceField(User, required=True, unique=True)
    hero = EmbeddedDocumentField(BackgroundImage)
    portfolio = EmbeddedDocumentField(BackgroundImage)
    biography = EmbeddedDocumentField(BackgroundImage)
    meta = {'collection': 'backgrounds'}

    def to_json_dict(self):
        def image_dict(img):
            if not img:
                return None
            return {'sm': img.sm, 'md': img.md, 'lg': img.lg}

        return {
            '_id': str(self.id),
            'hero': image_dict(self.hero),
            'portfolio': image_dict(self.portfolio),
            'biography': image_dict(self.biography),
        }
