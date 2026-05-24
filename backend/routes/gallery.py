import os
from bson import ObjectId
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required
from mongoengine import DoesNotExist
from pydantic import ValidationError
from Schemas.gallery import GalleryIn
from models.gallery import Gallery, GalleryImage

gallery_bp = Blueprint('gallery', __name__)


@gallery_bp.route('/gallery', methods=['GET'])
def get_gallery():
    return jsonify([gallery.to_json_dict() for gallery in Gallery.objects()]), 200


@gallery_bp.route('/gallery', methods=['PUT'])
@jwt_required()
def update_galleries():
    if not request.is_json:
        return jsonify({"error": "invalid content-type"}), 415
    payload = request.get_json()
    try:
        galleries = [GalleryIn.model_validate(g) for g in payload]
    except ValidationError:
        return jsonify({"error": "invalid payload"}), 400
    for g in galleries:
        images = [GalleryImage(**img.model_dump()) for img in g.images]
        if g.id:
            Gallery.objects(id=g.id).update_one(
                set__slug=g.slug,
                set__title=g.title,
                set__order=g.order,
                set__images=images
            )
        else:
            Gallery(
                slug=g.slug,
                title=g.title,
                order=g.order,
                images=images
            ).save()
    return jsonify({'updated': True}), 200


@gallery_bp.route('/gallery/<id>', methods=['DELETE'])
@jwt_required()
def delete_gallery(id):
    if not ObjectId.is_valid(id):
        return jsonify({'error': 'Invalid ID'}), 400
    try:
        gallery = Gallery.objects.get(id=id)
        gallery.delete()
        return jsonify({'deleted': True}), 200
    except DoesNotExist:
        return jsonify({'error': 'Gallery not found'}), 404


@gallery_bp.route('/gallery/next-src', methods=['GET'])
@jwt_required()
def get_next_src():
    gallery_slug = request.args.get('gallerySlug')
    if not gallery_slug:
        return jsonify({'error': 'Missing gallerySlug'}), 400
    settings = current_app.config['settings']
    dest = os.path.join(settings.upload_folder, 'gallery', gallery_slug)
    os.makedirs(dest, exist_ok=True)

    existing = [f for f in os.listdir(dest) if f.endswith('.webp')]
    next_index = len(existing) + 1
    src = f"{gallery_slug}_{str(next_index).zfill(4)}.webp"

    return jsonify({'src': src}), 200
