from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import mongo
from helpers import handle_db_timeout


biography_bp = Blueprint('biography', __name__)


@handle_db_timeout
@biography_bp.route('/biography', methods=['GET'])
def get_biography():
    biography = mongo.db.biography.find_one()
    return jsonify({'biography': biography})

@handle_db_timeout
@biography_bp.route('/biography', methods=['PUT'])
@jwt_required()
def update_biography():
    data = request.get_json()
    data.pop('_id', None)
    mongo.db.biography.update_one({}, {'$set': data})
    return jsonify({'updated': True}), 200
