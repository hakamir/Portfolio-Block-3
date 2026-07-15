from functools import wraps

from bson import ObjectId
from flask import jsonify, request


def valid_object_id(*param_names):
    """
    Verify that the provided object IDs are valid.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            for name in param_names:
                value = kwargs.get(name)
                if value and not ObjectId.is_valid(value):
                    return jsonify({'error': 'Invalid ID'}), 400
            return fn(*args, **kwargs)
        return wrapper
    return decorator
