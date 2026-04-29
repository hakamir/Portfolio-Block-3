from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from helpers import handle_db_timeout
from models.biography import Biography
from datetime import datetime, timezone

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
    data['updatedAt'] = datetime.now(timezone.utc)
    update_data = {f"set__{key}": value for key, value in data.items()}
    if not update_data:
        return jsonify({'error': 'No data to update'}), 400
    Biography.objects.update_one(**update_data)
    return jsonify({'updated': True}), 200