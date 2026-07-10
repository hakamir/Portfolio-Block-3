import os
from bson import ObjectId
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity
from mongoengine import DoesNotExist
from middleware.roles import roles_required
from models.orphan_audio import OrphanAudio
from models.orphan_gallery import OrphanGallery
from models.user import User
from services.audio_service import upsert_track
from services.gallery_service import upsert_image
from utils.filesystem import cleanup_empty_dirs

orphans_bp = Blueprint('orphans', __name__)


# Audio orphans

@orphans_bp.route('/orphans/audio', methods=['GET'])
@roles_required('artist', 'admin')
def get_orphan_audio():
    identity = get_jwt_identity()
    user = User.objects(id=identity).first()
    orphans = OrphanAudio.objects(user=user).order_by('artist_title', 'album_title', 'track_number')
    return jsonify([o.to_json_dict() for o in orphans]), 200

@orphans_bp.route('/orphans/audio/<user_id>', methods=['GET'])
@roles_required('admin')
def get_orphan_audio_by_user(user_id):
    user = User.objects(id=user_id).first()
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    orphans = OrphanAudio.objects(user=user).order_by('artist_title', 'album_title', 'track_number')
    return jsonify([o.to_json_dict() for o in orphans]), 200

@orphans_bp.route('/orphans/audio', methods=['DELETE'])
@roles_required('artist', 'admin')
def delete_orphan_audio():
    settings = current_app.config['settings']
    identity = get_jwt_identity()
    user = User.objects(id=identity).first()
    data = request.get_json()

    if not data or 'ids' not in data or not isinstance(data['ids'], list):
        return jsonify({'error': 'Expected a list of ids'}), 400

    deleted = []
    for raw_id in data['ids']:
        if not ObjectId.is_valid(raw_id):
            continue
        try:
            orphan = OrphanAudio.objects.get(id=raw_id, user=user)
        except DoesNotExist:
            continue
        file_path = os.path.join(settings.upload_folder, 'audio', orphan.relative_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        orphan.delete()
        deleted.append(raw_id)

    cleanup_empty_dirs(os.path.join(settings.upload_folder, 'audio'))
    return jsonify({'deleted': deleted}), 200


@orphans_bp.route('/orphans/audio/rollback', methods=['POST'])
@roles_required('artist', 'admin')
def rollback_orphan_audio():
    settings = current_app.config['settings']
    identity = get_jwt_identity()
    user = User.objects(id=identity).first()
    data = request.get_json()

    if not data or 'ids' not in data or not isinstance(data['ids'], list):
        return jsonify({'error': 'Expected a list of ids'}), 400

    restored = []
    failed = []

    for raw_id in data['ids']:
        if not ObjectId.is_valid(raw_id):
            failed.append({'id': raw_id, 'title': raw_id, 'error': 'Invalid id'})
            continue
        try:
            orphan = OrphanAudio.objects.get(id=raw_id, user=user)
        except DoesNotExist:
            failed.append({'id': raw_id, 'title': raw_id, 'error': 'Orphan not found'})
            continue

        file_path = os.path.join(settings.upload_folder, 'audio', orphan.relative_path)
        if not os.path.exists(file_path):
            failed.append({'id': raw_id, 'title': orphan.track_title, 'error': 'File not found'})
            continue

        metadata = {
            'artist': orphan.artist_title,
            'album': orphan.album_title,
            'title': orphan.track_title,
            'track_number': orphan.track_number,
            'tags': list(orphan.tags),
        }

        try:
            upsert_track(user, orphan.artist_slug, orphan.album_slug, orphan.track_src, metadata)
            orphan.delete()
            restored.append(raw_id)
        except Exception as e:
            failed.append({'id': raw_id, 'title': orphan.track_title, 'error': str(e)})

    return jsonify({'restored': restored, 'failed': failed}), 200


# Gallery orphans

@orphans_bp.route('/orphans/gallery', methods=['GET'])
@roles_required('artist', 'admin')
def get_orphan_gallery():
    identity = get_jwt_identity()
    user = User.objects(id=identity).first()
    orphans = OrphanGallery.objects(user=user).order_by('gallery_title', 'image_order')
    return jsonify([o.to_json_dict() for o in orphans]), 200

@orphans_bp.route('/orphans/gallery/<user_id>', methods=['GET'])
@roles_required('admin')
def get_orphan_gallery_by_user(user_id):
    user = User.objects(id=user_id).first()
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    orphans = OrphanGallery.objects(user=user).order_by('gallery_title', 'image_order')
    return jsonify([o.to_json_dict() for o in orphans]), 200

@orphans_bp.route('/orphans/gallery', methods=['DELETE'])
@roles_required('artist', 'admin')
def delete_orphan_gallery():
    settings = current_app.config['settings']
    identity = get_jwt_identity()
    user = User.objects(id=identity).first()
    data = request.get_json()

    if not data or 'ids' not in data or not isinstance(data['ids'], list):
        return jsonify({'error': 'Expected a list of ids'}), 400

    deleted = []
    for raw_id in data['ids']:
        if not ObjectId.is_valid(raw_id):
            continue
        try:
            orphan = OrphanGallery.objects.get(id=raw_id, user=user)
        except DoesNotExist:
            continue
        file_path = os.path.join(settings.upload_folder, 'gallery', orphan.relative_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        orphan.delete()
        deleted.append(raw_id)

    cleanup_empty_dirs(os.path.join(settings.upload_folder, 'gallery'))
    return jsonify({'deleted': deleted}), 200


@orphans_bp.route('/orphans/gallery/rollback', methods=['POST'])
@roles_required('artist', 'admin')
def rollback_orphan_gallery():
    settings = current_app.config['settings']
    identity = get_jwt_identity()
    user = User.objects(id=identity).first()
    data = request.get_json()

    if not data or 'ids' not in data or not isinstance(data['ids'], list):
        return jsonify({'error': 'Expected a list of ids'}), 400

    restored = []
    failed = []

    for raw_id in data['ids']:
        if not ObjectId.is_valid(raw_id):
            failed.append({'id': raw_id, 'title': raw_id, 'error': 'Invalid id'})
            continue
        try:
            orphan = OrphanGallery.objects.get(id=raw_id, user=user)
        except DoesNotExist:
            failed.append({'id': raw_id, 'title': raw_id, 'error': 'Orphan not found'})
            continue

        file_path = os.path.join(settings.upload_folder, 'gallery', orphan.relative_path)
        if not os.path.exists(file_path):
            failed.append({'id': raw_id, 'title': orphan.image_title, 'error': 'File not found'})
            continue

        metadata = {
            'gallery_title': orphan.gallery_title,
            'title': orphan.image_title,
            'location': orphan.image_location,
            'date': orphan.image_date,
            'alt': orphan.image_alt,
            'order': orphan.image_order,
        }

        try:
            upsert_image(user, orphan.gallery_slug, orphan.image_src, metadata)
            orphan.delete()
            restored.append(raw_id)
        except Exception as e:
            failed.append({'id': raw_id, 'title': orphan.image_title, 'error': str(e)})

    return jsonify({'restored': restored, 'failed': failed}), 200
