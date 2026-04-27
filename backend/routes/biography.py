from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from helpers import handle_db_timeout
from models.biography import Biography


biography_bp = Blueprint('biography', __name__)


@handle_db_timeout
@biography_bp.route('/biography', methods=['GET'])
def get_biography():
    biography = Biography.objects.first()
    return jsonify({"biography": biography.to_json_dict()})

@handle_db_timeout
@biography_bp.route('/biography', methods=['PUT'])
@jwt_required()
def update_biography():
    data = request.get_json()
    data.pop('_id', None)
    Biography.objects.update_one({}, {'$set': data})
    return jsonify({'updated': True}), 200
