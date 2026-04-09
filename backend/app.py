import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from bson import ObjectId
from datetime import timedelta, datetime
import bcrypt
from pymongo.errors import ServerSelectionTimeoutError

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Portfolio?serverSelectionTimeoutMS=5000'
app.config['JWT_SECRET_KEY'] = 'secret'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)

CORS(app)
mongo = PyMongo(app)
jwt = JWTManager(app)

messages_col = mongo.db.messages
artists_col = mongo.db.artists

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

# --- Helpers --- #
def handle_db_timeout(fn):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ServerSelectionTimeoutError as e:
            return jsonify({'error': 'Cannot connect to database'}), 500
    return wrapper

def serialize(doc):
    doc['_id'] = str(doc['_id'])
    return doc


# --- Auth --- #
@handle_db_timeout
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = mongo.db.users.find_one({'email': data['email']})

    if not user or not bcrypt.checkpw(data.get('pwd', '').encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = create_access_token(identity=str(user['_id']))
    return jsonify({'token': token})


# --- Messages --- #
@handle_db_timeout
@app.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    messages = [serialize(message) for message in messages_col.find()]
    return jsonify(messages)

@handle_db_timeout
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    if 'date' in data and isinstance(data['date'], str):
        data['date'] = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
    result = messages_col.insert_one(data)
    return jsonify({'inserted_id': str(result.inserted_id)}), 201

@handle_db_timeout
@app.route('/messages/<id>', methods=['PATCH'])
@jwt_required()
def update_message(id):
    data = request.get_json()
    messages_col.update_one({'_id': ObjectId(id)}, {'$set': data})
    return jsonify({'updated': id}), 200

@handle_db_timeout
@app.route('/messages/<id>', methods=['DELETE'])
@jwt_required()
def delete_message(id):
    messages_col.delete_one({'_id': ObjectId(id)})
    return jsonify({'deleted': id}), 200


# --- Biography --- #
@handle_db_timeout
@app.route('/biography', methods=['GET'])
def get_biography():
    biography = mongo.db.biography.find_one()
    return jsonify({'biography': biography})

@handle_db_timeout
@app.route('/biography', methods=['PUT'])
def update_biography():
    data = request.get_json()
    data.pop('_id', None)
    mongo.db.biography.update_one({}, {'$set': data})
    return jsonify({'updated': True}), 200

@handle_db_timeout
@app.route('/artists', methods=['GET'])
def get_artists():
    artists = [serialize(artist) for artist in artists_col.find()]
    return jsonify(artists)

# --- Upload --- #
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
