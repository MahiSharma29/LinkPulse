import os

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .extensions import db, login_manager
from .security import init_csrf


def _database_uri() -> str:
    url = os.environ.get("DATABASE_URL", "sqlite:///linkpulse.db")
    # Some providers still hand out the legacy "postgres://" scheme.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-insecure-key"),
        SQLALCHEMY_DATABASE_URI=_database_uri(),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("FLASK_ENV") == "production",
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    if test_config:
        app.config.update(test_config)

    if os.environ.get("FLASK_ENV") == "production" and app.config["SECRET_KEY"] == "dev-only-insecure-key":
        raise RuntimeError("SECRET_KEY must be set in production")

    # Trust the reverse proxy (Render) so https URLs are generated correctly.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Log in to continue."
    init_csrf(app)

    from .auth import bp as auth_bp
    from .links import bp as links_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(links_bp)

    with app.app_context():
        db.create_all()

    return app
