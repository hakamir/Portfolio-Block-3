from flask import jsonify
from functools import wraps
from pymongo.errors import ServerSelectionTimeoutError
from mongoengine.errors import OperationError, NotUniqueError


def handle_db_timeout(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ServerSelectionTimeoutError as e:
            return jsonify({'error': 'Cannot connect to database'}), 500
        except NotUniqueError as e:
            return jsonify({'error': 'Duplicate entry'}), 409
        except OperationError as e:
            return jsonify({'error': 'Database operation failed'}), 500

    return wrapper


def serialize(doc):
    data = doc.to_mongo().to_dict()
    if '_id' in data:
        data['_id'] = str(data['_id'])
    return data
