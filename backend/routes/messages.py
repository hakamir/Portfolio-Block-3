from datetime import datetime, timezone
from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from mongoengine.errors import ValidationError, DoesNotExist
from helpers import handle_db_timeout
from extensions import limiter
from models.message import Message
from pydantic import ValidationError as PydanticValidationError
from Schemas.message import MessageIn

messages_bp = Blueprint('messages', __name__)


@messages_bp.route('/messages', methods=['GET'])
@jwt_required()
@handle_db_timeout
def get_messages():
    messages = Message.objects().order_by('-date')
    return jsonify([msg.to_json_dict() for msg in messages]), 200

@limiter.limit("1/minute")
@messages_bp.route('/messages', methods=['POST'])
@handle_db_timeout
def create_message():
    try:
        data = MessageIn.model_validate(request.get_json())
    except PydanticValidationError:
        return jsonify({'error': 'Invalid payload'}), 400
    if not data:
        return jsonify({'error': 'Missing JSON data'}), 400
    try:
        message = Message(
            name=data.name,
            email=data.email,
            message=data.message,
            date=datetime.now(timezone.utc),
            read=False,
            trashed=False
        )
        message.validate()
        message.save()
        return jsonify({'created': True}), 201
    except ValidationError:
        return jsonify({'error': 'Invalid data'}), 400

@messages_bp.route('/messages/<id>', methods=['PATCH'])
@jwt_required()
@handle_db_timeout
def update_message(id):
    data = request.get_json()
    try:
        Message.objects.get(id=id).update(**data)
        return jsonify({'updated': True}), 200
    except DoesNotExist:
        return jsonify({'error': 'Message not found'}), 404

@messages_bp.route('/messages/<id>', methods=['DELETE'])
@jwt_required()
@handle_db_timeout
def delete_message(id):
    if not ObjectId.is_valid(id):
        return jsonify({'error': 'Invalid ID'}), 400
    try:
        message = Message.objects.get(id=id)
        message.delete()
        return jsonify({'deleted': True}), 200
    except DoesNotExist:
        return jsonify({'error': 'Message not Found'}), 404
