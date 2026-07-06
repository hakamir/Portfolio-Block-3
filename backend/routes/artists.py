import os
from bson import ObjectId
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required
from mongoengine import ValidationError as MongoEngineValidationError, DoesNotExist
from pydantic import ValidationError as PydanticValidationError
from Schemas.artist import ArtistIn
from middleware.roles import roles_required
from models.artist import Artist, Track, Album
from utils.filesystem import write_id3_tags

artists_bp = Blueprint('artists', __name__)


@artists_bp.route('/artists', methods=['GET'])
def get_artists():
    return jsonify([artist.to_json_dict() for artist in Artist.objects()]), 200


@artists_bp.route('/artists', methods=['PUT'])
@roles_required('artist', 'admin')
def update_artists():
    if not request.is_json:
        return jsonify({'error': 'Invalid content-type'}), 415
    payload = request.get_json()
    if not isinstance(payload, list):
        return jsonify({'error': 'Expected a list of artists'}), 400
    try:
        artists = [ArtistIn.model_validate(artist) for artist in payload]
        for item in artists:
            albums = [
                Album(
                    slug=al.slug,
                    title=al.title,
                    order=al.order,
                    tracks=[Track(**t.model_dump()) for t in al.tracks]
                ) for al in item.albums
            ]
            if item.id:
                artist = Artist.objects.get(id=item.id)
                artist.slug = item.slug
                artist.title = item.title
                artist.order = item.order
                artist.albums = albums
                artist.save()
            else:
                Artist(
                    slug=item.slug,
                    title=item.title,
                    order=item.order,
                    albums=albums
                ).save()

            # Include metadata in audio files
            for album in item.albums:
                for track in album.tracks:
                    print(track.tags, flush=True)
                    settings = current_app.config['settings']
                    file_path = os.path.join(settings.upload_folder, 'audio', item.slug, album.slug, track.src)
                    if os.path.exists(file_path):
                        write_id3_tags(file_path, {
                            'artist': item.title,
                            'album': album.title,
                            'title': track.title,
                            'track_number': str(track.trackNumber),
                            'tags': ",".join(track.tags),
                        })

        return jsonify({'updated': True}), 200
    except PydanticValidationError:
        return jsonify({'error': 'Invalid payload'}), 400
    except MongoEngineValidationError:
        return jsonify({'error': 'invalid data'}), 400
    except DoesNotExist:
        return jsonify({'error': 'Artist not found'}), 404


@artists_bp.route('/artists/<id>', methods=['DELETE'])
@roles_required('artist', 'admin')
def delete_artist(id):
    if not ObjectId.is_valid(id):
        return jsonify({'error': 'Invalid ID'}), 400
    try:
        artist = Artist.objects.get(id=id)
        artist.delete()
        return jsonify({'deleted': True}), 200
    except DoesNotExist:
        return jsonify({'error': 'Artist not found'}), 404
