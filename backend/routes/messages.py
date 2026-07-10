from datetime import datetime, timezone
from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import ValidationError, DoesNotExist
from extensions import limiter
from middleware.roles import roles_required
from models.message import Message
from pydantic import ValidationError as PydanticValidationError
from Schemas.message import MessageIn, MessageUpdate
from models.user import User

messages_bp = Blueprint('messages', __name__)


@messages_bp.route('/messages', methods=['GET'])
@roles_required('artist', 'admin')
def get_messages():
    identity = get_jwt_identity()
    user = User.objects(id=identity).first()
    messages = Message.objects(user=user).order_by('-date')
    return jsonify([msg.to_json_dict() for msg in messages]), 200


@messages_bp.route('/messages', methods=['POST'])
@limiter.limit("1/minute")
def create_message():
    try:
        data = MessageIn.model_validate(request.get_json())
    except PydanticValidationError:
        return jsonify({'error': 'Invalid payload'}), 400

    user = User.objects(role='artist', is_active=True).first()

    if not user:
        return jsonify({'error': 'No active artist found'}), 404
    try:
        message = Message(
            user=user,
            name=data.name,
            email=data.email,
            message=data.message,
            date=datetime.now(timezone.utc),
            read=False,
            trashed=False,
            replied=False
        )
        message.validate()
        message.save()
        return jsonify({'created': True}), 201
    except ValidationError:
        return jsonify({'error': 'Invalid data'}), 400


@messages_bp.route('/messages/<id>', methods=['PATCH'])
@roles_required('artist', 'admin')
def update_message(id):
    identity = get_jwt_identity()
    user = User.objects(id=identity).first()

    try:
        data = MessageUpdate.model_validate(request.get_json())
    except PydanticValidationError:
        return jsonify({'error': 'Invalid payload'}), 400

    updates = data.model_dump(exclude_none=True)

    if not updates:
        return jsonify({'error': 'No fields to update'}), 400

    if updates.get('replied') is True:
        updates['replied_at'] = datetime.now(timezone.utc)
    else:
        updates['replied_at'] = None

    try:
        message = Message.objects.get(id=id, user=user)
        message.update(**{f'set__{key}': value for key, value in updates.items()})
        return jsonify({'updated': True}), 200
    except DoesNotExist:
        return jsonify({'error': 'Message not found'}), 404


@messages_bp.route('/messages/<id>', methods=['DELETE'])
@roles_required('artist', 'admin')
def delete_message(id):
    if not ObjectId.is_valid(id):
        return jsonify({'error': 'Invalid ID'}), 400

    identity = get_jwt_identity()
    user = User.objects(id=identity).first()

    try:
        message = Message.objects.get(id=id, user=user)
        message.delete()
        return jsonify({'deleted': True}), 200
    except DoesNotExist:
        return jsonify({'error': 'Message not Found'}), 404
