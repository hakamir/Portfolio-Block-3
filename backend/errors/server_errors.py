from flask import Blueprint, jsonify

server_errors_bp = Blueprint('server_errors', __name__)

@server_errors_bp.app_errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal server error"}), 500

@server_errors_bp.app_errorhandler(Exception)
def handle_generic_error(error):
    return jsonify({"error": "An unexpected error occurred"}), 500