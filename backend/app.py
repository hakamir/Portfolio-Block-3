import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import timedelta, datetime
import bcrypt
from pymongo.errors import ServerSelectionTimeoutError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address



app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Portfolio?serverSelectionTimeoutMS=5000'
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)
CORS(app)
limiter = Limiter(get_remote_address, app=app, default_limits=[])

mongo = PyMongo(app)
jwt = JWTManager(app)

messages_col = mongo.db.messages
artists_col = mongo.db.artists
galleries_col = mongo.db.galleries

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
@limiter.limit("5/minute")
def login():
    data = request.get_json()
    user = mongo.db.users.find_one({'email': data['email']})

    if not user or not bcrypt.checkpw(data.get('pwd', '').encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = create_access_token(identity=str(user['_id']))
    return jsonify({'token': token})

@handle_db_timeout
@app.route('/auth/password', methods=['PUT'])
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


# --- Messages --- #
@handle_db_timeout
@app.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    messages = [serialize(message) for message in messages_col.find()]
    return jsonify(messages)

@handle_db_timeout
@limiter.limit("1/minute")
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


 # --- Artists --- #
@handle_db_timeout
@app.route('/artists', methods=['GET'])
def get_artists():
    artists = [serialize(artist) for artist in artists_col.find()]
    return jsonify(artists), 200

@handle_db_timeout
@app.route('/artists', methods=['PUT'])
@jwt_required()
def update_artists():
    data = request.get_json()
    for artist in data:
        artist_id = artist.pop('_id', None)
        if artist_id:
            artists_col.update_one({'_id': ObjectId(artist_id)}, {'$set': artist})
        else:
            artists_col.insert_one(artist)
    return jsonify({'updated': True}), 200

@handle_db_timeout
@app.route('/artists/<id>', methods=['delete'])
@jwt_required()
def delete_artist(id):
    artists_col.delete_one({'_id': ObjectId(id)})
    return jsonify({'deleted': True}), 200


# --- Gallery --- #
@handle_db_timeout
@app.route('/gallery', methods=['GET'])
def get_gallery():
    gallery = [serialize(gallery) for gallery in galleries_col.find()]
    return jsonify(gallery), 200


# --- Upload --- #
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/audio/upload', methods=['POST'])
@jwt_required()
def upload_file():
    file = request.files['file']
    artist_slug = request.form.get('artistSlug')
    album_slug = request.form.get('albumSlug')
    track_src = request.form.get('trackSrc')

    if not file or not artist_slug or not album_slug or not track_src:
        return jsonify({'error': 'Missing required fields'}), 400

    dest = os.path.join(UPLOAD_FOLDER, 'audio', artist_slug, album_slug)
    os.makedirs(dest, exist_ok=True)
    file.save(os.path.join(dest, track_src))

    return jsonify({'uploaded': track_src}), 201

@handle_db_timeout
@app.route('/audio/orphans', methods=['GET'])
@jwt_required()
def get_orphan_files():
    tracked_files = set()
    for artist in artists_col.find():
        for album in artist.get('albums', []):
            for track in album.get('tracks', []):
                path = os.path.join(artist['slug'], album['slug'], track['src'])
                tracked_files.add(path)
                tracked_files.add(path.replace('\\', '/'))

    orphans = []
    audio_folder = os.path.join(UPLOAD_FOLDER, 'audio')
    for root, dirs, files in os.walk(audio_folder):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, audio_folder)
            relative_path = relative_path.replace('\\', '/')
            if relative_path not in tracked_files:
                orphans.append(relative_path)
    return jsonify(orphans), 200

@app.route('/audio/orphans', methods=['DELETE'])
@jwt_required()
def delete_orphan_files():
    data = request.get_json()
    files = data.get('files', [])
    deleted = []
    for file in files:
        full_path = os.path.join(UPLOAD_FOLDER, 'audio', file)
        if os.path.exists(full_path):
            os.remove(full_path)
            deleted.append(file)

    # Clean up empty directories
    audio_folder = os.path.join(UPLOAD_FOLDER, 'audio')
    for root, dirs, files in os.walk(audio_folder, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
    return jsonify({'deleted': deleted}), 200

if __name__ == '__main__':
    app.run(debug=True)
