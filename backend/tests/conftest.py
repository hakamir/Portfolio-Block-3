import mongomock
import pytest
from flask_jwt_extended import create_access_token
from mongoengine import connect as me_connect, disconnect
from mongoengine.connection import get_db
from unittest.mock import patch

from app import create_app
from config import Settings
from models.user import User


class TestSettings(Settings):
    frontend_url: str = "http://localhost"
    frontend_port: int = 3000
    mongodb_user: str = "test"
    mongodb_password: str = "test"
    mongodb_host: str = "localhost"
    mongodb_port: int = 27017
    mongodb_database: str = "testdb"
    mongodb_timeout: int = 500
    jwt_secret_key: str = "test-secret-key-for-testing-only"
    jwt_access_token_expires: int = 15
    jwt_refresh_token_expires: int = 30
    jwt_cookie_secure: bool = False
    jwt_cookie_samesite: str = "Lax"
    jwt_cookie_csrf_protect: bool = False

    class Config:
        env_file = None
        case_sensitive = False


def _init_db_mock(_settings):
    me_connect('testdb', mongo_client_class=mongomock.MongoClient)


@pytest.fixture(scope="session")
def app():
    with patch('app.init_db', _init_db_mock):
        flask_app = create_app(settings=TestSettings(), testing=True)
    yield flask_app
    disconnect()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def test_artist_user(app):
    with app.app_context():
        user = User(
            email="artist@test.com",
            password="hashed_password",
            role="artist",
            is_active=True
        ).save()
    return user


@pytest.fixture
def test_admin_user(app):
    with app.app_context():
        user = User(
            email="admin@test.com",
            password="hashed_password",
            role="admin",
            is_active=False
        ).save()
    return user


@pytest.fixture
def auth_headers(app, test_artist_user):
    with app.app_context():
        token = create_access_token(
            identity=str(test_artist_user.id),
            additional_claims={'role': 'artist'}
        )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(app, test_admin_user):
    with app.app_context():
        token = create_access_token(
            identity=str(test_admin_user.id),
            additional_claims={'role': 'admin'}
        )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def clean_db(app):
    yield
    db = get_db()
    for name in db.list_collection_names():
        db.drop_collection(name)
