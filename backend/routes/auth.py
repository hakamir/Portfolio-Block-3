import bcrypt
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token, \
    set_refresh_cookies, unset_jwt_cookies
from mongoengine import DoesNotExist
from pydantic import ValidationError
from werkzeug.exceptions import UnsupportedMediaType
from Schemas.auth import Login, PasswordUpdate
from extensions import limiter
from middleware.roles import roles_required
from models.user import User

auth_bp = Blueprint('auth', __name__)

_DUMMY_HASH = bcrypt.hashpw(b"dummy", bcrypt.gensalt()).decode()


@auth_bp.route('/auth/login', methods=['POST'])
@limiter.limit("5/minute")
def login():
    try:
        data = Login.model_validate(request.get_json())
        try:
            user = User.objects.get(email=data.email)
        except DoesNotExist:
            bcrypt.checkpw(data.pwd.encode('utf-8'), _DUMMY_HASH.encode('utf-8'))
            return jsonify({'error': 'Invalid credentials'}), 401

        if not user.verify_password(data.pwd):
            raise DoesNotExist

        access_token = create_access_token(identity=str(user.id), additional_claims={'role': user.role})
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
def refresh():
    identity = get_jwt_identity()
    user = User.objects.get(id=identity)
    if not user:
        return jsonify({'error': 'user not found'}), 404
    new_access_token = create_access_token(identity=identity, additional_claims={'role': user.role})
    return jsonify({'token': new_access_token}), 200


@auth_bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({'logged_out': True})
    #TODO: Blacklist refresh token here (Redis)
    unset_jwt_cookies(response)
    return response, 200


@auth_bp.route('/auth/password', methods=['PUT'])
@roles_required('artist', 'admin')
@limiter.limit("1/minute")
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
        errors = []
        for err in e.errors():
            loc = err.get('loc', ())
            field = loc[0] if len(loc) > 0 else 'model_error'
            errors.append({"field": field, "message": err.get('msg').replace('Value error, ', '')})

        return jsonify({'error': {'Invalid payload': errors}}), 400

