import os
from flask import Blueprint, jsonify, request, send_from_directory, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from middleware.roles import roles_required
from utils.AudioConverter import AudioConverter
from utils.filesystem import write_id3_tags
from utils.image_validation import is_valid_webp

uploads_bp = Blueprint('uploads', __name__)


@uploads_bp.route('/upload/<path:filename>')
def get_file(filename):
    download = request.args.get('download') == 'true'
    settings = current_app.config['settings']
    return send_from_directory(settings.upload_folder, filename, as_attachment=download)


@uploads_bp.route('/upload/audio', methods=['POST'])
@roles_required('artist', 'admin')
def upload_audio():
    settings = current_app.config['settings']
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if not file.mimetype.startswith('audio/'):
        return jsonify({'error': 'Invalid mime type'}), 415

    # Champs techniques (sauvegarde du fichier)
    artist_slug = secure_filename(request.form.get('artistSlug', ''))
    album_slug = secure_filename(request.form.get('albumSlug', ''))
    track_src = secure_filename(request.form.get('trackSrc', ''))

    # Champs metadata (tags ID3)
    artist_title = request.form.get('artistTitle', artist_slug)
    album_title = request.form.get('albumTitle', album_slug)
    track_title = request.form.get('trackTitle', track_src.rsplit('.', 1)[0])
    track_number = request.form.get('trackNumber', '0')
    track_tags = request.form.get('trackTags', '')
    extension = file.filename.rsplit('.', 1)[-1].lower()
    if extension not in settings.allowed_audio_file_types:
        return jsonify({'error': 'Invalid file type'}), 415

    if not file or not artist_slug or not album_slug or not track_src:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        file = AudioConverter.to_mp3(file, extension)
    except ValueError:
        return jsonify({'error': "File conversion failed"}), 500

    dest = os.path.join(settings.upload_folder, 'audio', artist_slug, album_slug)
    os.makedirs(dest, exist_ok=True)
    final_path = os.path.join(dest, track_src)
    file.save(final_path)

    write_id3_tags(filepath=final_path, metadata={
        'artist': artist_title,
        'album': album_title,
        'title': track_title,
        'track_number': track_number,
        'tags': track_tags
    })

    return jsonify({'uploaded': True}), 201


@uploads_bp.route('/upload/gallery', methods=['POST'])
@roles_required('artist', 'admin')
def upload_image():
    settings = current_app.config['settings']

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if not file.mimetype.startswith('image/'):
        return jsonify({'error': 'Invalid mime type'}), 415

    gallery_slug = secure_filename(request.form.get('gallerySlug', ''))
    image_src = secure_filename(request.form.get('imageSrc', ''))

    extension = file.filename.split('.', 1)[-1].lower()
    if extension not in settings.allowed_image_file_types:
        return jsonify({'error': 'Invalid file type'}), 415

    if not file or not gallery_slug or not image_src:
        return jsonify({'error': 'Missing required fields'}), 400

    dest = os.path.join(settings.upload_folder, 'gallery', gallery_slug)
    os.makedirs(dest, exist_ok=True)
    file.save(os.path.join(dest, image_src))
    return jsonify({'uploaded': True}), 201


@uploads_bp.route('/upload/background', methods=['POST'])
@roles_required('artist', 'admin')
def upload_background():
    destination = request.form.get('destination')
    file_2048 = request.files.get('image-2048')
    file_1024 = request.files.get('image-1024')
    file_512 = request.files.get('image-512')

    if not destination or not file_2048 or not file_1024 or not file_512:
        return jsonify({'error': 'Missing required fields'}), 400

    files = [file_2048, file_1024, file_512]
    if not all(is_valid_webp(f) for f in files):
        return jsonify({'error': 'Invalid file'}), 400

    settings = current_app.config['settings']

    if destination == 'hero' or destination == 'portfolio':
        dest = os.path.join(settings.upload_folder, 'background/', destination)
        file_2048.save(f'{dest}/{destination}-2048.webp')
        file_1024.save(f'{dest}/{destination}-1024.webp')
        file_512.save(f'{dest}/{destination}-512.webp')
        return jsonify({'uploaded': True}), 201
    elif destination == 'biography':
        dest = os.path.join(settings.upload_folder, f'/{destination}')
        file_2048.save(f'{dest}/{destination}-1-2048.webp')
        file_1024.save(f'{dest}/{destination}-1-1024.webp')
        file_512.save(f'{dest}/{destination}-1-512.webp')
        return jsonify({'uploaded': True}), 201
    else:
        return jsonify({'error': 'Invalid destination'}), 400
