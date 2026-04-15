from bson import ObjectId
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import mongo, limiter
from helpers import handle_db_timeout, serialize


messages_bp = Blueprint('messages', __name__)


@handle_db_timeout
@messages_bp.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    messages = [serialize(message) for message in mongo.db.messages.find()]
    return jsonify(messages)

@handle_db_timeout
@limiter.limit("1/minute")
@messages_bp.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    if 'date' in data and isinstance(data['date'], str):
        data['date'] = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
    result = mongo.db.messages.insert_one(data)
    return jsonify({'inserted_id': str(result.inserted_id)}), 201

@handle_db_timeout
@messages_bp.route('/messages/<id>', methods=['PATCH'])
@jwt_required()
def update_message(id):
    data = request.get_json()
    mongo.db.messages.update_one({'_id': ObjectId(id)}, {'$set': data})
    return jsonify({'updated': id}), 200

@handle_db_timeout
@messages_bp.route('/messages/<id>', methods=['DELETE'])
@jwt_required()
def delete_message(id):
    mongo.db.messages.delete_one({'_id': ObjectId(id)})
    return jsonify({'deleted': id}), 200
