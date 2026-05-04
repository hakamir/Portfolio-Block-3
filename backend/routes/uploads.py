import os
from flask import Blueprint, jsonify, request, send_from_directory, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from helpers import handle_db_timeout, AudioConverter
from models.artist import Artist

uploads_bp = Blueprint('uploads', __name__)


@uploads_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    settings = current_app.config['settings']
    return send_from_directory(settings.upload_folder, filename)


@uploads_bp.route('/audio/upload', methods=['POST'])
@jwt_required()
def upload_audio():
    settings = current_app.config['settings']
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if not file.mimetype.startswith('audio/'):
        return jsonify({'error': 'Invalid mime type'}), 415

    artist_slug = secure_filename(request.form.get('artistSlug'))
    album_slug = secure_filename(request.form.get('albumSlug'))
    track_src = secure_filename(request.form.get('trackSrc'))

    extension = file.filename.rsplit('.', 1)[-1].lower()
    if extension not in settings.allowed_audio_file_types:
        return jsonify({'error': 'Invalid file type'}), 415

    if not file or not artist_slug or not album_slug or not track_src:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        file = AudioConverter.to_mp3(file, extension)
        extension = 'mp3'
        track_src = track_src.replace(f'.{extension}', '.mp3')
    except ValueError:
        return jsonify({'error': "File conversion failed"}), 500

    dest = os.path.join(settings.upload_folder, 'audio', artist_slug, album_slug)
    os.makedirs(dest, exist_ok=True)
    file.save(os.path.join(dest, track_src))

    return jsonify({'uploaded': True}), 201


@uploads_bp.route('/audio/orphans', methods=['GET'])
@jwt_required()
@handle_db_timeout
def get_orphan_audio():
    settings = current_app.config['settings']
    tracked_files = set()
    for artist in Artist.objects():
        for album in artist.albums:
            for track in album.tracks:
                path = os.path.join(artist.slug, album.slug, track.src)
                tracked_files.add(path)
                tracked_files.add(path.replace('\\', '/'))

    orphans = []
    audio_folder = os.path.join(settings.upload_folder, 'audio')
    for root, dirs, files in os.walk(audio_folder):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, audio_folder)
            relative_path = relative_path.replace('\\', '/')
            if relative_path not in tracked_files:
                orphans.append(relative_path)
    return jsonify(orphans), 200


@uploads_bp.route('/audio/orphans', methods=['DELETE'])
@jwt_required()
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
    audio_folder = os.path.join(settings.upload_folder, 'audio')
    for root, dirs, files in os.walk(audio_folder, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
    return jsonify({'deleted': deleted}), 200


@uploads_bp.route('/gallery/upload', methods=['POST'])
@jwt_required()
def upload_image():
    settings = current_app.config['settings']

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files.get('file')

    if not file or file.filename is None:
        return jsonify({'error': 'Missing file'}), 400

    gallery_slug = secure_filename(request.form.get('gallerySlug'))
    image_src = secure_filename(request.form.get('imageSrc'))

    extension = file.filename.split('.', 1)[-1].lower()
    if extension not in settings.allowed_image_file_types:
        return jsonify({'error': 'Invalid file type'}), 400

    if not file or not gallery_slug or not image_src:
        return jsonify({'error': 'Missing data'}), 400

    dest = os.path.join(settings.upload_folder, 'gallery', gallery_slug)
    os.makedirs(dest, exist_ok=True)
    file.save(os.path.join(dest, image_src))
    return jsonify({'uploaded': image_src}), 201
