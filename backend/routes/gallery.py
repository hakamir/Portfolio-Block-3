import os
from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from config import Config
from extensions import mongo
from helpers import handle_db_timeout, serialize


gallery_bp = Blueprint('gallery', __name__)


@handle_db_timeout
@gallery_bp.route('/gallery', methods=['GET'])
def get_gallery():
    gallery = [serialize(gallery) for gallery in mongo.db.galleries.find()]
    return jsonify(gallery), 200

@handle_db_timeout
@gallery_bp.route('/gallery', methods=['PUT'])
@jwt_required()
def update_galleries():
    data = request.get_json()
    for gallery in data:
        gallery_id = gallery.pop('_id', None)
        if gallery_id:
            mongo.db.galleries.update_one(
                {'_id': ObjectId(gallery_id)},
                {'$set': gallery}
            )
        else:
            mongo.db.galleries.insert_one(gallery)
    return jsonify({'updated': True}), 200

@handle_db_timeout
@gallery_bp.route('/gallery/<id>', methods=['DELETE'])
@jwt_required()
def delete_gallery(id):
    mongo.db.galleries.delete_one({'_id': ObjectId(id)})
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
