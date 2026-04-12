from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import mongo
from helpers import handle_db_timeout, serialize


artists_bp = Blueprint('artists', __name__)


@handle_db_timeout
@artists_bp.route('/artists', methods=['GET'])
def get_artists():
    artists = [serialize(artist) for artist in mongo.db.artists.find()]
    return jsonify(artists), 200

@handle_db_timeout
@artists_bp.route('/artists', methods=['PUT'])
@jwt_required()
def update_artists():
    data = request.get_json()
    for artist in data:
        artist_id = artist.pop('_id', None)
        if artist_id:
            mongo.db.artists.update_one({'_id': ObjectId(artist_id)}, {'$set': artist})
        else:
            mongo.db.artists.insert_one(artist)
    return jsonify({'updated': True}), 200

@handle_db_timeout
@artists_bp.route('/artists/<id>', methods=['delete'])
@jwt_required()
def delete_artist(id):
    mongo.db.artists.delete_one({'_id': ObjectId(id)})
    return jsonify({'deleted': True}), 200
