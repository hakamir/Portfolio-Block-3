from errors.http_errors import http_errors_bp
from errors.db_errors import db_errors_bp


def register_errors(app):
    app.register_blueprint(http_errors_bp)
    app.register_blueprint(db_errors_bp)