import os
from bson import ObjectId
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required
from mongoengine import DoesNotExist, ValidationError as MongoEngineValidationError
from pydantic import ValidationError as PydanticValidationError
from Schemas.gallery import GalleryIn
from middleware.roles import roles_required
from models.gallery import Gallery, GalleryImage

gallery_bp = Blueprint('gallery', __name__)


@gallery_bp.route('/gallery', methods=['GET'])
def get_gallery():
    return jsonify([gallery.to_json_dict() for gallery in Gallery.objects()]), 200


@gallery_bp.route('/gallery', methods=['PUT'])
@roles_required('artist', 'admin')
def update_galleries():
    if not request.is_json:
        return jsonify({"error": "invalid content-type"}), 415
    payload = request.get_json()
    if not isinstance(payload, list):
        return jsonify({'error': 'Expected a list of galleries'}), 400
    try:
        galleries = [GalleryIn.model_validate(g) for g in payload]

        for g in galleries:
            images = [GalleryImage(**img.model_dump()) for img in g.images]
            if g.id:
                gallery = Gallery.objects.get(id=g.id)
                gallery.slug = g.slug
                gallery.title = g.title
                gallery.order = g.order
                gallery.images = images
                gallery.save()
            else:
                Gallery(
                    slug=g.slug,
                    title=g.title,
                    order=g.order,
                    images=images
                ).save()
        return jsonify({'updated': True}), 200
    except PydanticValidationError as e:
        errors = []
        for err in e.errors():
            loc = err.get('loc', ())
            field = loc[0] if len(loc) > 0 else 'model_error'
            errors.append({"field": field, "message": err.get('msg').replace('Value error, ', '')})

        return jsonify({'error': {'Invalid payload': errors}}), 400

    except MongoEngineValidationError:
        return jsonify({'error': 'invalid data'}), 400
    except DoesNotExist:
        return jsonify({'error': 'Gallery not found'}), 404


@gallery_bp.route('/gallery/<id>', methods=['DELETE'])
@roles_required('artist', 'admin')
def delete_gallery(id):
    if not ObjectId.is_valid(id):
        return jsonify({'error': 'Invalid ID'}), 400
    try:
        gallery = Gallery.objects.get(id=id)
        gallery.delete()
        return jsonify({'deleted': True}), 200
    except DoesNotExist:
        return jsonify({'error': 'Gallery not found'}), 404
