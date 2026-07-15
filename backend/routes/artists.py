from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import get_jwt_identity
from mongoengine import ValidationError as MongoEngineValidationError, DoesNotExist
from pydantic import ValidationError as PydanticValidationError
from Schemas.artist import ArtistIn
from middleware.roles import roles_required
from middleware.validators import valid_object_id
from models.artist import Artist
from models.user import User
from services.artist_service import orphan_removed_tracks, orphan_all_tracks, build_albums, sync_id3_tags
from uuid import uuid4

artists_bp = Blueprint('artists', __name__)


@artists_bp.route('/artists', methods=['GET'])
def get_active_artists():
    """Get tracks of the active artist. Public."""
    active_user = User.objects(role='artist', is_active=True).first()
    if not active_user:
        return jsonify([]), 200
    return jsonify([artist.to_json_dict() for artist in Artist.objects(user=active_user)]), 200


@artists_bp.route('/artists/dashboard', methods=['GET'])
@roles_required('artist', 'admin')
def get_owned_artists():
    """Get tracks owned by the authenticated user."""
    identity = get_jwt_identity()
    user = User.objects(id=identity).first()
    return jsonify([artist.to_json_dict() for artist in Artist.objects(user=user)]), 200


@artists_bp.route('/artists/<user_id>', methods=['GET'])
@roles_required('admin')
@valid_object_id('user_id')
def get_artist_by_user_id(user_id: str):
    """Get tracks from a specific user. Admin only."""
    user = User.objects(id=user_id).first()
    if user is None:
        return jsonify({"error": "user not found"}), 404
    return jsonify([artist.to_json_dict() for artist in Artist.objects(user=user)]), 200


@artists_bp.route('/artists', methods=['PUT'])
@roles_required('artist', 'admin')
def update_owned_artists():
    """Update tracks of the authenticated artist. Applicative bulk upsert."""
    if not request.is_json:
        return jsonify({'error': 'Invalid content-type'}), 415
    payload = request.get_json()
    if not isinstance(payload, list):
        return jsonify({'error': 'Expected a list of artists'}), 400
    try:
        identity = get_jwt_identity()
        user = User.objects(id=identity).first()
        artists_input = [ArtistIn.model_validate(a) for a in payload]
        settings = current_app.config['settings']

        result = []
        for item in artists_input:
            if item.id:
                artist = Artist.objects.get(id=item.id, user=user)
                orphan_removed_tracks(user, artist, item.albums, settings.upload_folder)
            else:
                artist = None

            albums = build_albums(item.albums, artist)

            if artist:
                artist.title = item.title
                artist.order = item.order
                artist.albums = albums
                artist.save()
            else:
                artist = Artist(
                    user=user,
                    slug=str(uuid4()),
                    title=item.title,
                    order=item.order,
                    albums=albums,
                )
                artist.save()

            sync_id3_tags(artist, settings.upload_folder)
            result.append(artist.to_json_dict())

        return jsonify(result), 200
    except PydanticValidationError:
        return jsonify({'error': 'Invalid payload'}), 400
    except MongoEngineValidationError:
        return jsonify({'error': 'invalid data'}), 400
    except DoesNotExist:
        return jsonify({'error': 'Artist not found'}), 404


@artists_bp.route('/artists/<artist_id>', methods=['DELETE'])
@roles_required('artist', 'admin')
@valid_object_id('artist_id')
def delete_artist(artist_id):
    """Delete an artist document. Can only delete documents owned by the authenticated user."""
    identity = get_jwt_identity()
    user = User.objects(id=identity).first()
    try:
        artist = Artist.objects.get(id=artist_id, user=user)
        settings = current_app.config['settings']
        orphan_all_tracks(user, artist, settings.upload_folder)
        artist.delete()
        return jsonify({'deleted': True}), 200
    except DoesNotExist:
        return jsonify({'error': 'Artist not found'}), 404
