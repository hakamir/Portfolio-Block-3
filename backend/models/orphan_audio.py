from mongoengine import ReferenceField, Document, ObjectIdField, StringField, IntField, ListField, DateTimeField

from models.user import User


class OrphanAudio(Document):
    user = ReferenceField(User, required=True)
    artist_id = ObjectIdField(null=True)
    artist_slug = StringField(required=True)
    artist_title = StringField(required=True)
    album_slug = StringField(required=True)
    album_title = StringField(required=True)
    track_title = StringField(required=True)
    track_src = StringField(required=True)
    track_number = IntField(required=True)
    tags = ListField(StringField())
    deleted_at = DateTimeField(required=True)
    meta = {'collection': 'orphan_audios'}

    @property
    def relative_path(self):
        return f'{self.artist_slug}/{self.album_slug}/{self.track_src}'

    def to_json_dict(self):
        return {
            '_id': str(self.id),
            'artist_title': self.artist_title,
            'album_title': self.album_title,
            'track_title': self.track_title,
            'track_number': self.track_number,
            'src': self.relative_path,
            'tags': list(self.tags),
            'deleted_at': self.deleted_at,
        }
