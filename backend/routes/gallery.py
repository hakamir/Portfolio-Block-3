import os
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from config import Config
from helpers import handle_db_timeout
from models.gallery import Gallery

gallery_bp = Blueprint('gallery', __name__)


@gallery_bp.route('/gallery', methods=['GET'])
@handle_db_timeout
def get_gallery():
    return jsonify([gallery.to_json_dict() for gallery in Gallery.objects()]), 200

@gallery_bp.route('/gallery', methods=['PUT'])
@jwt_required()
@handle_db_timeout
def update_galleries():
    data = request.get_json()
    for gallery in data:
        gallery_id = gallery.pop('_id', None)
        if gallery_id:
            Gallery.objects(id=gallery_id).update_one(
                **gallery
            )
        else:
            Gallery(**gallery).save()
    return jsonify({'updated': True}), 200

@gallery_bp.route('/gallery/<id>', methods=['DELETE'])
@jwt_required()
@handle_db_timeout
def delete_gallery(id):
    Gallery.objects(id=id).delete()
    return jsonify({'deleted': id}), 200

@gallery_bp.route('/gallery/upload', methods=['POST'])
@jwt_required()
def upload_image():
    file = request.files.get('file')
    gallery_slug = request.form.get('gallerySlug')
    image_src = request.form.get('imageSrc')

    if not file or not gallery_slug or not image_src:
        return jsonify({'error': 'Missing data'}), 400

    dest = os.path.join(Config.UPLOAD_FOLDER, 'gallery', gallery_slug)
    os.makedirs(dest, exist_ok=True)
    file.save(os.path.join(dest, image_src))
    return jsonify({'uploaded': image_src}), 201

@gallery_bp.route('/gallery/next-src', methods=['GET'])
@jwt_required()
def get_next_src():
    gallery_slug = request.args.get('gallerySlug')
    if not gallery_slug:
        return jsonify({'error': 'Missing gallerySlug'}), 400

    dest = os.path.join(Config.UPLOAD_FOLDER, 'gallery', gallery_slug)
    os.makedirs(dest, exist_ok=True)

    existing = [f for f in os.listdir(dest) if f.endswith('.webp')]
    next_index = len(existing) + 1
    src = f"{gallery_slug}_{str(next_index).zfill(4)}.webp"

    return jsonify({'src': src}), 200
