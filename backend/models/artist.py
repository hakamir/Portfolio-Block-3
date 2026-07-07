from mongoengine import EmbeddedDocument, IntField, StringField, ListField, EmbeddedDocumentField, Document, \
    ValidationError, ReferenceField

from models.user import User


class Track(EmbeddedDocument):
    trackNumber = IntField(required=True)
    title = StringField(required=True)
    src = StringField(required=True)
    tags = ListField(StringField())


class Album(EmbeddedDocument):
    slug = StringField(required=True)
    title = StringField(required=True)
    order = IntField(required=True)
    tracks = ListField(EmbeddedDocumentField(Track))


class Artist(Document):
    user = ReferenceField(User, required=True)
    slug = StringField(required=True)
    title = StringField(required=True)
    order = IntField(required=True)
    albums = ListField(EmbeddedDocumentField(Album))
    meta = {'collection': 'artists'}

    def to_json_dict(self):
        data = self.to_mongo().to_dict()
        data['_id'] = str(data['_id'])
        data.pop('user')
        return data

    def clean(self):
        if not self.title:
            raise ValidationError('Artist title is required')

        if not self.slug:
            raise ValidationError('Artist slug is required')

        if not self.order:
            raise ValidationError('Artist order is required')

        if not self.albums:
            raise ValidationError('Artist must have at least one album')

        for album in self.albums:
            album.clean()

        for album in self.albums:
            if not album.title:
                raise ValidationError('Album title is required')
            if not album.slug:
                raise ValidationError('Album slug is required')
            if not album.order:
                raise ValidationError('Album order is required')
            if not album.tracks:
                raise ValidationError('Album must have at least one track')

            for track in album.tracks:
                if not track.title:
                    raise ValidationError('Track title is required')
                if not track.src:
                    raise ValidationError('Track source is required')
                if not track.trackNumber:
                    raise ValidationError('Track number is required')

                if track.trackNumber <= 0:
                    raise ValidationError('Track order must be positive')