import os
from flask import Blueprint, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required

from config import Config
from extensions import mongo
from helpers import handle_db_timeout


uploads_bp = Blueprint('uploads', __name__)


@uploads_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

@uploads_bp.route('/audio/upload', methods=['POST'])
@jwt_required()
def upload_file():
    file = request.files['file']
    artist_slug = request.form.get('artistSlug')
    album_slug = request.form.get('albumSlug')
    track_src = request.form.get('trackSrc')

    if not file or not artist_slug or not album_slug or not track_src:
        return jsonify({'error': 'Missing required fields'}), 400

    dest = os.path.join(Config.UPLOAD_FOLDER, 'audio', artist_slug, album_slug)
    os.makedirs(dest, exist_ok=True)
    file.save(os.path.join(dest, track_src))

    return jsonify({'uploaded': track_src}), 201

@handle_db_timeout
@uploads_bp.route('/audio/orphans', methods=['GET'])
@jwt_required()
def get_orphan_files():
    tracked_files = set()
    for artist in mongo.db.artists.find():
        for album in artist.get('albums', []):
            for track in album.get('tracks', []):
                path = os.path.join(artist['slug'], album['slug'], track['src'])
                tracked_files.add(path)
                tracked_files.add(path.replace('\\', '/'))

    orphans = []
    audio_folder = os.path.join(Config.UPLOAD_FOLDER, 'audio')
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
def delete_orphan_files():
    data = request.get_json()
    files = data.get('files', [])
    deleted = []
    for file in files:
        full_path = os.path.join(Config.UPLOAD_FOLDER, 'audio', file)
        if os.path.exists(full_path):
            os.remove(full_path)
            deleted.append(file)

    # Clean up empty directories
    audio_folder = os.path.join(Config.UPLOAD_FOLDER, 'audio')
    for root, dirs, files in os.walk(audio_folder, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
    return jsonify({'deleted': deleted}), 200
