import bcrypt
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token, decode_token, \
    set_refresh_cookies, unset_jwt_cookies
from mongoengine import DoesNotExist
from pydantic import ValidationError
from werkzeug.exceptions import UnsupportedMediaType
from Schemas.auth import Login, PasswordUpdate
from extensions import limiter
from helpers import handle_db_timeout
from models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth/login', methods=['POST'])
@limiter.limit("5/minute")
@handle_db_timeout
def login():
    try:
        data = Login.model_validate(request.get_json())
        user = User.objects.get(email=data.email)
        if not user.verify_password(data.pwd):
            raise DoesNotExist

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        response = jsonify({'token': access_token})
        set_refresh_cookies(response, refresh_token)
        return response, 200

    except (DoesNotExist, ValidationError):
        return jsonify({'error': 'Invalid credentials'}), 401
    except UnsupportedMediaType:
        return jsonify({'error': "content-type must be application/json"}), 415


@auth_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
@handle_db_timeout
def refresh():
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify({'token': new_access_token}), 200


@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    response = jsonify({'logged_out': True})
    unset_jwt_cookies(response)
    return response, 200

@auth_bp.route('/auth/password', methods=['PUT'])
@jwt_required()
@limiter.limit("5/minute")
@handle_db_timeout
def update_password():
    try:
        data = PasswordUpdate.model_validate(request.get_json())
        user = User.objects.get(id=get_jwt_identity())
        if not user.verify_password(data.currentPwd):
            return jsonify({'error': 'Invalid credentials'}), 401

        hashed = bcrypt.hashpw(data.newPwd.encode('utf-8'), bcrypt.gensalt())
        user.password = hashed.decode('utf-8')
        user.save()
        return jsonify({'updated': True}), 200
    except UnsupportedMediaType:
        return jsonify({'error': "content-type must be application/json"}), 415
    except DoesNotExist:
        return jsonify({'error': 'user not found'}), 404
    except ValidationError as e:
        errors = {
            err['loc'][0]: err['msg'].replace('Value error, ', '')
            for err in e.errors()
        }
        return jsonify({'error': {'Invalid payload': errors}}), 400
