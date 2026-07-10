import os
from bson import ObjectId
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import get_jwt_identity
from mongoengine import ValidationError as MongoEngineValidationError, DoesNotExist
from pydantic import ValidationError as PydanticValidationError
from Schemas.artist import ArtistIn
from middleware.roles import roles_required
from models.artist import Artist, Track, Album
from models.user import User
from utils.filesystem import write_id3_tags
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
        artist_input = [ArtistIn.model_validate(artist) for artist in payload]

        result = []
        for item in artist_input:
            # Resolve artist slug
            if item.id:
                artist = Artist.objects.get(id=item.id, user=user)
                artist_slug = artist.slug
            else:
                artist_slug = str(uuid4())
                artist = None

            # Build album with slug resolution
            existing_album_slug = {album.slug: album for album in artist.albums} if artist else {}

            albums = []
            for album in item.albums:
                if album.slug and album.slug in existing_album_slug:
                    album_slug = album.slug
                    existing_track = {track.src: track for track in existing_album_slug[album.slug].tracks}
                else:
                    album_slug = str(uuid4())
                    existing_track = {}

                # Build tracks with src resolution
                tracks = []
                for track in album.tracks:
                    if track.src and track.src in existing_track:
                        track_src = track.src
                    else:
                        track_src = str(uuid4()) + '.mp3'

                    tracks.append(Track(
                        trackNumber=track.trackNumber,
                        title=track.title,
                        src=track_src,
                        tags=track.tags,
                    ))
                albums.append(Album(
                    slug=album_slug,
                    title=album.title,
                    order=album.order,
                    tracks=tracks,
                ))

            # Save artist
            if artist:
                artist.slug = artist_slug
                artist.title = item.title
                artist.order = item.order
                artist.albums = albums
                artist.save()
            else:
                artist = Artist(
                    user=user,
                    slug=artist_slug,
                    title=item.title,
                    order=item.order,
                    albums=albums,
                )
                artist.save()

            # Write ID3 tags in existing files
            settings = current_app.config['settings']
            for album in artist.albums:
                for track in album.tracks:
                    file_path = os.path.join(
                        settings.upload_folder, 'audio',
                        artist.slug, album.slug, track.src
                    )
                    if os.path.exists(file_path):
                        write_id3_tags(file_path, {
                            'artist': artist.title,
                            'album': album.title,
                            'title': track.title,
                            'track_number': str(track.trackNumber),
                            'tags': ','.join(track.tags),
                        })

            result.append(artist.to_json_dict())

        return jsonify(result), 200
    except PydanticValidationError:
        return jsonify({'error': 'Invalid payload'}), 400
    except MongoEngineValidationError:
        return jsonify({'error': 'invalid data'}), 400
    except DoesNotExist:
        return jsonify({'error': 'Artist not found'}), 404


@artists_bp.route('/artists/<id>', methods=['DELETE'])
@roles_required('artist', 'admin')
def delete_artist(id):
    """
    Delete a document (artist) from the artists' collection by its ID.
    Can only delete documents owned by the authenticated user.
    """
    if not ObjectId.is_valid(id):
        return jsonify({'error': 'Invalid ID'}), 400
    identity = get_jwt_identity()
    user = User.objects(id=identity).first()
    try:
        artist = Artist.objects.get(id=id, user=user)
        artist.delete()
        return jsonify({'deleted': True}), 200
    except DoesNotExist:
        return jsonify({'error': 'Artist not found'}), 404
