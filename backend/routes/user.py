import bcrypt
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from mongoengine import ValidationError as MongoEngineValidationError, DoesNotExist
from pydantic import ValidationError as PydanticValidationError
from Schemas.user import CreateUser
from middleware.roles import roles_required
from middleware.validators import valid_object_id
from models.user import User
from utils.background import create_default_background

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
@roles_required('admin')
def get_user():
    users = User.objects()
    return jsonify([user.to_json_dict() for user in users]), 200


@user_bp.route('/users/<user_id>', methods=['GET'])
@roles_required('admin')
@valid_object_id('user_id')
def get_user_by_id(user_id):
    try:
        user = User.objects.get(id=user_id)
        return jsonify(
            user.to_json_dict()
        )
    except DoesNotExist:
        return jsonify({'error': 'User not found'}), 404
    except MongoEngineValidationError:
        return jsonify({'error': 'Invalid ID'}), 400


@user_bp.route('/users/active', methods=['GET'])
@roles_required('admin')
def get_active_user():
    user = User.objects(role="artist", is_active=True).first()
    if not user:
        return jsonify({'error': 'No active users'}), 404
    return jsonify(user.to_json_dict()), 200


@user_bp.route('/users', methods=['POST'])
@roles_required('admin')
def create_user():
    try:
        data = CreateUser.model_validate(request.get_json())
    except PydanticValidationError as e:
        return jsonify({'error': "Invalid payload"}), 400
    if User.objects(email=data.email).first():
        return jsonify({'error': 'Email already exists'}), 409
    try:
        hashed = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt())
        user = User(
            email=data.email,
            password=hashed.decode('utf-8'),
            role=data.role
        )
        user.validate()
        user.save()

        if user.role == 'artist':
            create_default_background(user)

        return jsonify({'created': True}), 201
    except MongoEngineValidationError:
        return jsonify({'error': 'Invalid data'}), 400


@user_bp.route('/users/<user_id>', methods=['DELETE'])
@roles_required('admin')
@valid_object_id('user_id')
def delete_user(user_id):
    identity = get_jwt_identity()
    if identity == user_id:
        return jsonify({'error': 'Cannot delete own account'}), 400
    try:
        user = User.objects.get(id=user_id)
    except DoesNotExist:
        return jsonify({'error': 'User not found'}), 404
    except MongoEngineValidationError:
        return jsonify({'error': 'Invalid ID'}), 400
    if user.is_active:
        return jsonify({'error': 'Cannot delete active user'}), 400
    user.delete()
    return jsonify(None), 204


@user_bp.route('/users/<user_id>/role', methods=['PUT'])
@roles_required('admin')
@valid_object_id('user_id')
def update_role(user_id: str):
    identity = get_jwt_identity()
    if identity == user_id:
        return jsonify({'error': 'Cannot update own role'}), 400
    try:
        user = User.objects.get(id=user_id)
        if user.is_active:
            return jsonify({'error': 'Cannot update role of active user'}), 400
    except DoesNotExist:
        return jsonify({'error': 'User not found'}), 404
    except MongoEngineValidationError:
        return jsonify({'error': 'Invalid ID'}), 400
    data = request.get_json()
    if not data or 'role' not in data:
        return jsonify({'error': 'Missing role field'}), 400
    role = data.get('role')
    if role not in ['artist', 'admin']:
        return jsonify({'error': 'Invalid role'}), 400
    try:
        user.role = role
        user.save()
    except MongoEngineValidationError:
        return jsonify({'error': "Invalid payload"}), 400
    return jsonify({'updated': True}), 200


@user_bp.route('/users/<user_id>/activate', methods=['PUT'])
@roles_required('admin')
@valid_object_id('user_id')
def activate_user(user_id: str):
    try:
        user = User.objects(id=user_id, role='artist').first()
    except MongoEngineValidationError:
        return jsonify({'error': 'Invalid ID'}), 400
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if user.is_active:
        return jsonify({'error': 'User is already active'}), 400
    User.objects(role='artist').update(set__is_active=False)
    User.objects(id=user_id).update(set__is_active=True)
    return jsonify({'activated': True}), 200
