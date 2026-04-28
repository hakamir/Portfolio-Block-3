from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from helpers import handle_db_timeout
from models.biography import Biography


biography_bp = Blueprint('biography', __name__)


@biography_bp.route('/biography', methods=['GET'])
@handle_db_timeout
def get_biography():
    biography = Biography.objects.first()
    return jsonify({"biography": biography.to_json_dict()})

@biography_bp.route('/biography', methods=['PUT'])
@jwt_required()
@handle_db_timeout
def update_biography():
    data = request.get_json()
    data.pop('_id', None)
    Biography.objects.update_one({}, {'$set': data})
    return jsonify({'updated': True}), 200
