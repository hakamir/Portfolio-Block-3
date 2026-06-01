from .auth import auth_bp
from .messages import messages_bp
from .biography import biography_bp
from .artists import artists_bp
from .gallery import gallery_bp
from .uploads import uploads_bp
from .orphans import orphans_bp


def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(messages_bp, url_prefix='/api')
    app.register_blueprint(biography_bp, url_prefix='/api')
    app.register_blueprint(artists_bp, url_prefix='/api')
    app.register_blueprint(gallery_bp, url_prefix='/api')
    app.register_blueprint(uploads_bp, url_prefix='/api')
    app.register_blueprint(orphans_bp, url_prefix='/api')
