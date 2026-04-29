from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from mongoengine import ValidationError, DoesNotExist
from pydantic import ValidationError as PydanticValidationError
from Schemas.artist import ArtistIn
from helpers import handle_db_timeout
from models.artist import Artist, Track, Album

artists_bp = Blueprint('artists', __name__)


@artists_bp.route('/artists', methods=['GET'])
@handle_db_timeout
def get_artists():
    return jsonify([artist.to_json_dict() for artist in Artist.objects()]), 200


@artists_bp.route('/artists', methods=['PUT'])
@jwt_required()
@handle_db_timeout
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
        return jsonify({'updated': True}), 200
    except PydanticValidationError as e:
        return jsonify({'error': 'Invalid payload'}), 400
    except ValidationError:
        return jsonify({'error': 'invalid data'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': 'Server error'}), 500


@artists_bp.route('/artists/<id>', methods=['DELETE'])
@jwt_required()
@handle_db_timeout
def delete_artist(id):
    if not ObjectId.is_valid(id):
        return jsonify({'error': 'Invalid ID'}), 400
    try:
        artist = Artist.objects.get(id=id)
        artist.delete()
        return jsonify({'deleted': True}), 200
    except DoesNotExist:
        return jsonify({'error': 'Artist not found'}), 404
