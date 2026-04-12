from flask import jsonify
from pymongo.errors import ServerSelectionTimeoutError


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
