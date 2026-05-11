import os
from flask import Blueprint, jsonify, request, send_from_directory, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from models.artist import Artist
from models.gallery import Gallery
from utils.AudioConverter import AudioConverter
from utils.decorators import handle_db_timeout
from utils.filesystem import cleanup_empty_dirs, get_files

uploads_bp = Blueprint('uploads', __name__)


@uploads_bp.route('/upload/<path:filename>')
def uploaded_file(filename):
    settings = current_app.config['settings']
    return send_from_directory(settings.upload_folder, filename)


@uploads_bp.route('/upload/audio', methods=['POST'])
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


@uploads_bp.route('/orphans/audio', methods=['GET'])
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

    # Get all files in the audio folder
    orphans = get_files(os.path.join(settings.upload_folder, 'audio'), tracked_files)
    return jsonify(orphans), 200


@uploads_bp.route('/orphans/audio', methods=['DELETE'])
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
    cleanup_empty_dirs(os.path.join(settings.upload_folder, 'audio'))
    return jsonify({'deleted': deleted}), 200


@uploads_bp.route('/upload/gallery', methods=['POST'])
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

@uploads_bp.route('/orphans/gallery', methods=['GET'])
@jwt_required()
@handle_db_timeout
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

@uploads_bp.route('/orphans/gallery', methods=['DELETE'])
@jwt_required()
@handle_db_timeout
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
    return jsonify({'deleted': deleted}), 200
