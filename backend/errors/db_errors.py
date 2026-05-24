from flask import Blueprint, jsonify
from mongoengine import NotUniqueError, OperationError
from pymongo.errors import ServerSelectionTimeoutError

db_errors_bp = Blueprint('db_errors', __name__)

@db_errors_bp.app_errorhandler(ServerSelectionTimeoutError)
def db_timeout(error):
    return jsonify({"error": "Database connection timeout"}), 503

@db_errors_bp.app_errorhandler(NotUniqueError)
def unique_error(error):
    return jsonify({'error': 'Duplicate entry'}), 409

@db_errors_bp.app_errorhandler(OperationError)
def db_error(error):
    return jsonify({'error': 'Database operation failed'}), 500
