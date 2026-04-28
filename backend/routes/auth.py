import bcrypt
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from extensions import limiter
from helpers import handle_db_timeout
from models.user import User


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth/login', methods=['POST'])
@limiter.limit("5/minute")
@handle_db_timeout
def login():
    data = request.get_json()
    user = User.objects.get(email=data['email'])
    if not user or not bcrypt.checkpw(data.get('pwd', '').encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token})

@auth_bp.route('/auth/password', methods=['PUT'])
@jwt_required()
@handle_db_timeout
def update_password():
    try:
        data = request.get_json()
        user = User.objects.get(id=get_jwt_identity())
        if not bcrypt.checkpw(data['currentPwd'].encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({'error': 'Invalid current password'}), 401

        hashed = bcrypt.hashpw(data['newPwd'].encode('utf-8'), bcrypt.gensalt())
        user.password = hashed.decode('utf-8')
        user.save()
        return jsonify({'updated': True}), 200
    except Exception as e:
        print('error:', e)
        return jsonify({'error': str(e)}), 500
