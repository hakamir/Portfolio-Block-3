from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from mongoengine import ValidationError, DoesNotExist

from helpers import handle_db_timeout
from extensions import limiter
from models.message import Message


messages_bp = Blueprint('messages', __name__)


@handle_db_timeout
@messages_bp.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    messages = Message.objects().order_by('-date')
    return jsonify([msg.to_json_dict() for msg in messages]), 200

@handle_db_timeout
@limiter.limit("1/minute")
@messages_bp.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    if 'date' in data and isinstance(data['date'], str):
        data['date'] = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
    try:
        message = Message(**data)
        message.validate()
        message.save()
        return jsonify({'inserted_id': str(message.id)}), 201
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400

@handle_db_timeout
@messages_bp.route('/messages/<id>', methods=['PATCH'])
@jwt_required()
def update_message(id):
    data = request.get_json()
    try:
        Message.objects.get(id=id).update(**data)
        return jsonify({'updated': id}), 200
    except DoesNotExist:
        return jsonify({'error': 'Message not found'}), 404

@handle_db_timeout
@messages_bp.route('/messages/<id>', methods=['DELETE'])
@jwt_required()
def delete_message(id):
    try:
        Message.objects.get(id=id).delete()
        return jsonify({'deleted': id}), 200
    except DoesNotExist:
        return jsonify({'error': 'Message not Found'}), 404
