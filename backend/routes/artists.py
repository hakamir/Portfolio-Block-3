from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from mongoengine import ValidationError, DoesNotExist, InvalidQueryError

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
    data = request.get_json()

    if not data or not isinstance(data, list):
        return jsonify({'error': 'Expected a list of artists'}), 400

    try:
        for artist_data in data:
            artist_data = dict(artist_data)
            artist_id = artist_data.pop('_id', None)

            albums = []
            for album_data in artist_data.pop('albums', []):
                album_data = dict(album_data)
                tracks = [Track(**t) for t in album_data.pop('tracks', [])]
                albums.append(Album(tracks=tracks, **album_data))

            artist_obj = Artist(albums=albums, **artist_data)
            artist_obj.validate()

            if artist_id:
                doc = artist_obj.to_mongo().to_dict()
                doc.pop('_id', None)

                result = Artist._get_collection().replace_one(
                    {'_id': ObjectId(artist_id)},
                    doc
                )
                if result.matched_count == 0:
                    return jsonify({'error': f'Artist {artist_id} not found'}), 404
            else:
                artist_obj.save()

        return jsonify({'updated': True}), 200

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@artists_bp.route('/artists/<id>', methods=['DELETE'])
@jwt_required()
@handle_db_timeout
def delete_artist(id):
    try:
        artist = Artist.objects.get(id=id)
        artist.delete()
        return jsonify({'deleted': True}), 200
    except DoesNotExist:
        return jsonify({'error': 'Artist not found'}), 404
