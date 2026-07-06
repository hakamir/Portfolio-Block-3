import bcrypt
from flask import Blueprint, jsonify, request
from mongoengine import ValidationError as MongoEngineValidationError
from pydantic import ValidationError as PydanticValidationError

from Schemas.user import CreateUser
from middleware.roles import roles_required
from models.user import User

user_bp = Blueprint('users', __name__)

@user_bp.route('/users', methods=['GET'])
@roles_required('admin')
def get_user():
    users = User.objects()
    return jsonify([user.to_json_dict() for user in users]), 200

@user_bp.route('/users/<id>', methods=['GET'])
@roles_required('admin')
def get_user_by_id(id):
    try:
        user = User.objects.get(id=id)
        return jsonify(
            user.to_json_dict()
        )
    except User.DoesNotExist:
        return jsonify({'error': 'User not found'}), 404

@user_bp.route('/users', methods=['POST'])
@roles_required('admin')
def create_user():
    try:
        data = CreateUser.model_validate(request.get_json())
    except PydanticValidationError as e:
        return jsonify({'error': str(e)}), 400
    if not data:
        return jsonify({'error': 'Missing JSON data'}), 400
    try:
        hashed = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt())
        user = User(
            firstname=data.firstname,
            lastname=data.lastname,
            email=data.email,
            password=hashed,
            role=data.role
        )
        user.validate()
        user.save()
        return jsonify({'created': True}), 201
    except MongoEngineValidationError as e:
        print(str(e), flush=True)
        return jsonify({'error': 'Invalid data'}), 400

@user_bp.route('/users/<id>', methods=['DELETE'])
@roles_required('admin')
def delete_user(id):
    user = User.objects.get(id=id)
    user.delete()
    return jsonify(None), 204