from flask import Blueprint, jsonify


http_errors_bp = Blueprint('errors', __name__)


@http_errors_bp.app_errorhandler(403)
def forbidden(error):
    return jsonify({"error": "Forbidden"}), 403


@http_errors_bp.app_errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@http_errors_bp.app_errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405


@http_errors_bp.app_errorhandler(429)
def too_many_requests(error):
    return jsonify({"error": "Too many requests"}), 429
