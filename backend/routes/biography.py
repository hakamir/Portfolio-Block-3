from flask import Blueprint, jsonify, request
from mongoengine import DoesNotExist, ValidationError
from pydantic import ValidationError as PydanticValidationError
from Schemas.biography import BiographyIn
from middleware.roles import roles_required
from models.biography import Biography, ImageSize, Section
from datetime import datetime, timezone

biography_bp = Blueprint('biography', __name__)


@biography_bp.route('/biography', methods=['GET'])
def get_biography():
    biography = Biography.objects.first()
    if biography is None:
        return jsonify({"error": "biography not found"}), 404
    return jsonify({"biography": biography.to_json_dict()})


@biography_bp.route('/biography', methods=['PUT'])
@roles_required('artist', 'admin')
def update_biography():
    if not request.is_json:
        return jsonify({"error": "invalid content-type"}), 415
    try:
        data = BiographyIn.model_validate(request.get_json())
    except PydanticValidationError:
        return jsonify({"error": "invalid payload"}), 400
    try:
        bio = Biography.objects.get(id=data.id)
        bio.title = data.title
        bio.image = ImageSize(**data.image.model_dump())
        bio.sections = [Section(**s.model_dump()) for s in data.sections]
        bio.updatedAt = datetime.now(timezone.utc)
        bio.save()
        return jsonify({"updated": True}), 200
    except DoesNotExist:
        return jsonify({"error": "biography not found"}), 404
    except ValidationError:
        return jsonify({"error": "invalid ID"}), 400

@biography_bp.route('/biography', methods=['POST'])
@roles_required('admin')
def create_biography():
    biography = Biography.objects.first()
    if biography is not None:
        return jsonify({"error": "biography already exists"}), 400
    try:
        data = BiographyIn.model_validate(request.get_json())
    except PydanticValidationError:
        return jsonify({"error": "invalid payload"}), 400
    try:
        Biography(**data.model_dump()).save()
        return jsonify({"created": True}), 201
    except ValidationError:
        return jsonify({"error": "invalid payload"}), 400