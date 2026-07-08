from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from mongoengine import DoesNotExist, ValidationError as MongoEngineValidationError
from pydantic import ValidationError as PydanticValidationError
from Schemas.biography import BiographyIn, BiographyCreateIn
from middleware.roles import roles_required
from models.biography import Biography, Section
from datetime import datetime, timezone
from models.user import User

biography_bp = Blueprint('biography', __name__)


@biography_bp.route('/biography', methods=['GET'])
def get_active_biography():
    """Get the biography of the active artist. Public."""
    artist = User.objects(role='artist', is_active=True).first()
    biography = Biography.objects(user=artist).first()
    if biography is None:
        return jsonify({"error": "biography not found"}), 404
    return jsonify({"biography": biography.to_json_dict()})


@biography_bp.route('/biography/dashboard', methods=['GET'])
@roles_required('artist', 'admin')
def get_owned_biography():
    """Get the biography owned by the authenticated user."""
    identity = get_jwt_identity()
    user = User.objects(id=identity).first()
    biography = Biography.objects(user=user).first()
    if biography is None:
        return jsonify({"error": "biography not found"}), 404
    return jsonify({"biography": biography.to_json_dict()})


@biography_bp.route('/biography/<user_id>', methods=['GET'])
@roles_required('admin')
def get_biography_by_user_id(user_id: str):
    """Get the biography of a specific user. Admin only."""
    user = User.objects(id=user_id).first()
    if user is None:
        return jsonify({"error": "user not found"}), 404
    biography = Biography.objects(user=user).first()
    if biography is None:
        return jsonify({"error": "biography not found"}), 404
    return jsonify({"biography": biography.to_json_dict()})


@biography_bp.route('/biography', methods=['PUT'])
@roles_required('artist', 'admin')
def update_biography():
    """Update biography of the authenticated artist."""
    identity = get_jwt_identity()
    user = User.objects(id=identity).first()
    if not request.is_json:
        return jsonify({"error": "invalid content-type"}), 415
    try:
        data = BiographyIn.model_validate(request.get_json())
    except PydanticValidationError:
        return jsonify({"error": "invalid payload"}), 400
    try:
        bio = Biography.objects.get(id=data.id, user=user)
        bio.title = data.title
        bio.sections = [Section(**s.model_dump()) for s in data.sections]
        bio.updatedAt = datetime.now(timezone.utc)
        bio.save()
        return jsonify({"updated": True}), 200
    except DoesNotExist:
        return jsonify({"error": "biography not found"}), 404
    except MongoEngineValidationError:
        return jsonify({"error": "invalid ID"}), 400


@biography_bp.route('/biography', methods=['POST'])
@roles_required('admin')
def create_biography():
    """Create a new biography for a specific artist."""
    if not request.is_json:
        return jsonify({"error": "invalid content-type"}), 415
    try:
        data = BiographyCreateIn.model_validate(request.get_json())
    except PydanticValidationError:
        return jsonify({"error": "invalid payload"}), 400
    target_user = User.objects(id=data.user_id, role='artist').first()
    if not target_user:
        return jsonify({"error": "user not found"}), 404
    if Biography.objects(user=target_user).first():
        return jsonify({"error": "biography already exists"}), 409
    try:
        Biography(
            user=target_user,
            title=data.title,
            sections=[
                Section(title=s.title, paragraphs=s.paragraphs)
                for s in data.sections
            ]
        ).save()
        return jsonify({"created": True}), 201
    except MongoEngineValidationError:
        return jsonify({"error": "invalid payload"}), 400


@biography_bp.route('/biography/<user_id>', methods=['DELETE'])
@roles_required('admin')
def delete_biography(user_id):
    """Delete a biography of a specific user. Admin only."""
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"error": "user not found"}), 404
    try:
        biography = Biography.objects.get(user=user)
        biography.delete()
        return jsonify(), 204
    except DoesNotExist:
        return jsonify({"error": "biography not found"}), 404
