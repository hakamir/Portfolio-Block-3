import os
from flask import Blueprint, current_app, jsonify, request
from middleware.roles import roles_required
from models.artist import Artist
from services.audio_service import upsert_track
from models.gallery import Gallery
from utils.filesystem import cleanup_empty_dirs, get_files, read_id3_tags

orphans_bp = Blueprint('orphans', __name__)


@orphans_bp.route('/orphans/audio', methods=['GET'])
@roles_required('artist', 'admin')
def get_orphan_audio():
    settings = current_app.config['settings']
    tracked_files = set()
    for artist in Artist.objects():
        for album in artist.albums:
            for track in album.tracks:
                path = os.path.join(artist.slug, album.slug, track.src)
                tracked_files.add(path)
                tracked_files.add(path.replace('\\', '/'))

    # Get all files in the audio folder
    audio_folder = os.path.join(settings.upload_folder, 'audio')
    orphans_paths = get_files(audio_folder, tracked_files)

    result = []
    for relative_path in orphans_paths:
        full_path = os.path.join(audio_folder, relative_path)
        metadata = read_id3_tags(full_path)
        result.append({
            'file': relative_path,
            'metadata': metadata
        })
    return jsonify(result), 200


@orphans_bp.route('/orphans/audio', methods=['DELETE'])
@roles_required('artist', 'admin')
def delete_orphan_audio():
    settings = current_app.config['settings']
    data = request.get_json()
    files = data.get('files', [])
    deleted = []
    for file in files:

        full_path = os.path.join(settings.upload_folder, 'audio', file)
        if os.path.exists(full_path):
            os.remove(full_path)
            deleted.append(file)

    # Clean up empty directories
    cleanup_empty_dirs(os.path.join(settings.upload_folder, 'audio'))
    return jsonify({'deleted': True}), 200


@orphans_bp.route('/orphans/audio/rollback', methods=['POST'])
@roles_required('artist', 'admin')
def rollback_orphan_audio():
    settings = current_app.config['settings']
    data = request.get_json()

    if not data or 'files' not in data or not isinstance(data['files'], list):
        return jsonify({'error': 'Expected a list of files'}), 400

    restored = []
    failed = []

    for relative_path in data['files']:
        full_path = os.path.join(settings.upload_folder, 'audio', relative_path)

        if not os.path.exists(full_path):
            failed.append({'file': relative_path, 'error': 'File not found'})
            continue

        metadata = read_id3_tags(full_path)

        if not metadata:
            failed.append({'file': relative_path, 'error': 'No ID3 metadata found'})
            continue

        parts = relative_path.replace('\\', '/').split('/')
        if len(parts) != 3:
            failed.append({'file': relative_path, 'error': 'Unexpected path structure'})
            continue

        artist_slug, album_slug, track_src = parts

        try:
            upsert_track(artist_slug, album_slug, track_src, metadata)
            restored.append(relative_path)
        except Exception as e:
            failed.append({'file': relative_path, 'error': str(e)})
    return jsonify({'restored': restored, 'failed': failed}), 200


@orphans_bp.route('/orphans/gallery', methods=['GET'])
@roles_required('artist', 'admin')
def get_orphan_gallery():
    settings = current_app.config['settings']
    tracked_files = set()
    for gallery in Gallery.objects():
        for image in gallery.images:
            path = os.path.join(gallery.slug, image.src)
            tracked_files.add(path)
            tracked_files.add(path.replace('\\', '/'))

    # Get all files in the gallery folder
    orphans = get_files(os.path.join(settings.upload_folder, 'gallery'), tracked_files)
    return jsonify(orphans), 200


@orphans_bp.route('/orphans/gallery', methods=['DELETE'])
@roles_required('artist', 'admin')
def delete_orphan_gallery():
    settings = current_app.config['settings']
    data = request.get_json()
    files = data.get('files', [])
    deleted = []
    for file in files:
        full_path = os.path.join(settings.upload_folder, 'gallery', file)
        if os.path.exists(full_path):
            os.remove(full_path)
            deleted.append(file)

    # Clean up empty directories
    cleanup_empty_dirs(os.path.join(settings.upload_folder, 'gallery'))
    return jsonify({'deleted': True}), 200
