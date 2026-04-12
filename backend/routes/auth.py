import bcrypt
from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from extensions import mongo, limiter
from helpers import handle_db_timeout


auth_bp = Blueprint('auth', __name__)


@handle_db_timeout
@auth_bp.route('/auth/login', methods=['POST'])
@limiter.limit("5/minute")
def login():
    data = request.get_json()
    user = mongo.db.users.find_one({'email': data['email']})

    if not user or not bcrypt.checkpw(data.get('pwd', '').encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = create_access_token(identity=str(user['_id']))
    return jsonify({'token': token})

@handle_db_timeout
@auth_bp.route('/auth/password', methods=['PUT'])
@jwt_required()
def update_password():
    try:
        data = request.get_json()
        print('data: ', data)
        user = mongo.db.users.find_one({'_id': ObjectId(get_jwt_identity())})
        print('user: ', user)
        if not bcrypt.checkpw(data['currentPwd'].encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'error': 'Invalid current password'}), 401

        hashed = bcrypt.hashpw(data['newPwd'].encode('utf-8'), bcrypt.gensalt())
        mongo.db.users.update_one({'_id': user['_id']}, {'$set': {'password': hashed.decode('utf-8')}})
        return jsonify({'updated': True}), 200
    except Exception as e:
        print('error:', e)
        return jsonify({'error': str(e)}), 500
