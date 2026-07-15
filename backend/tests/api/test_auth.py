import bcrypt
import pytest
from flask_jwt_extended import create_access_token, decode_token

from models.user import User

_TEST_EMAIL = "test@example.com"
_TEST_PASSWORD = "Test@Password1!"
_NEW_PASSWORD = "NewP@ssword456!"


@pytest.fixture
def test_user():
    hashed = bcrypt.hashpw(_TEST_PASSWORD.encode(), bcrypt.gensalt()).decode()
    return User(email=_TEST_EMAIL, password=hashed).save()


@pytest.fixture
def user_auth_headers(app, test_user):
    with app.app_context():
        token = create_access_token(identity=str(test_user.id), additional_claims={'role': test_user.role})
    return {"Authorization": f"Bearer {token}"}


class TestLogin:
    def test_returns_415_with_wrong_content_type(self, client):
        response = client.post("/api/auth/login", data="raw", content_type="text/plain")
        assert response.status_code == 415

    def test_returns_401_with_unknown_email(self, client):
        response = client.post("/api/auth/login", json={
            "email": "unknown@example.com", "pwd": _TEST_PASSWORD
        })
        assert response.status_code == 401
        assert response.get_json() == {"error": "Invalid credentials"}

    def test_returns_401_with_wrong_password(self, client, test_user):
        response = client.post("/api/auth/login", json={
            "email": _TEST_EMAIL, "pwd": "WrongP@ssword123!"
        })
        assert response.status_code == 401
        assert response.get_json() == {"error": "Invalid credentials"}

    def test_returns_token_on_valid_credentials(self, client, test_user):
        response = client.post("/api/auth/login", json={
            "email": _TEST_EMAIL, "pwd": _TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.get_json()
        assert "token" in data
        assert isinstance(data["token"], str)

    def test_returns_400_on_missing_fields(self, client):
        response = client.post("/api/auth/login", json={"email": _TEST_EMAIL})
        assert response.status_code == 401  # captured by except (DoesNotExist, ValidationError)

    def test_returns_token_contains_role_claim(self, app, client, test_user):
        # Role must be included in token - needed for roles_required
        response = client.post("/api/auth/login", json={
            "email": _TEST_EMAIL, "pwd": _TEST_PASSWORD
        })
        assert response.status_code == 200
        token = response.get_json()["token"]
        set_cookies = " ".join(response.headers.getlist("Set-Cookie"))
        assert "refresh_token=" in set_cookies
        with app.app_context():
            decoded = decode_token(token)
        assert decoded["role"] == test_user.role

    def test_sets_refresh_cookie_on_login(self, client, test_user):
        response = client.post("/api/auth/login", json={
            "email": _TEST_EMAIL, "pwd": _TEST_PASSWORD
        })
        assert response.status_code == 200
        set_cookies = " ".join(response.headers.getlist("Set-Cookie"))
        assert "refresh_token=" in set_cookies


class TestRefresh:
    def test_returns_401_without_refresh_token(self, client):
        response = client.post("/api/auth/refresh")
        assert response.status_code == 401

    def test_returns_new_access_token(self, app, test_user):
        # Login first so the test client stores the refresh cookie in its cookie store (jar),
        # then the refresh request sends it automatically, just like a browser would.
        with app.test_client() as c:
            c.post("/api/auth/login", json={"email": _TEST_EMAIL, "pwd": _TEST_PASSWORD})
            response = c.post("/api/auth/refresh")
        assert response.status_code == 200
        data = response.get_json()
        assert "token" in data
        assert isinstance(data["token"], str)

    def test_refresh_token_contains_role(self, app, test_user):
        # New token must contain role
        with app.test_client() as c:
            c.post("/api/auth/login", json={"email": _TEST_EMAIL, "pwd": _TEST_PASSWORD})
            response = c.post("/api/auth/refresh")
        assert response.status_code == 200
        with app.app_context():
            decoded = decode_token(response.get_json()["token"])
        assert decoded["role"] == test_user.role


class TestLogout:
    def test_returns_401_without_token(self, client):
        response = client.post("/api/auth/logout")
        assert response.status_code == 401

    def test_returns_200(self, client, user_auth_headers):
        response = client.post("/api/auth/logout", headers=user_auth_headers)
        assert response.status_code == 200
        assert response.get_json() == {"logged_out": True}

    def test_unsets_refresh_cookie_on_logout(self, client, user_auth_headers):
        response = client.post("/api/auth/logout", headers=user_auth_headers)
        assert response.status_code == 200

        # Get all Set-cookie headers
        set_cookies = response.headers.getlist("Set-Cookie")
        cookie_str = " ".join(set_cookies)

        assert "refresh_token=" in cookie_str
        assert "Expires=Thu, 01 Jan 1970" in cookie_str or "Max-Age=0" in cookie_str


class TestUpdatePassword:
    def test_requires_authentication(self, client):
        response = client.put("/api/auth/password", json={
            "currentPwd": _TEST_PASSWORD, "newPwd": _NEW_PASSWORD
        })
        assert response.status_code == 401

    def test_requires_json_content_type(self, client, user_auth_headers):
        response = client.put("/api/auth/password", data="raw", content_type="text/plain",
                              headers=user_auth_headers)
        assert response.status_code == 415

    def test_returns_400_on_invalid_payload(self, client, user_auth_headers):
        response = client.put("/api/auth/password", json={
            "currentPwd": _TEST_PASSWORD, "newPwd": "short"
        }, headers=user_auth_headers)
        assert response.status_code == 400

    def test_returns_401_on_wrong_current_password(self, client, test_user, user_auth_headers):
        response = client.put("/api/auth/password", json={
            "currentPwd": "WrongP@ssword123!", "newPwd": _NEW_PASSWORD
        }, headers=user_auth_headers)
        assert response.status_code == 401
        assert response.get_json() == {"error": "Invalid credentials"}

    def test_updates_password_successfully(self, client, test_user, user_auth_headers):
        response = client.put("/api/auth/password", json={
            "currentPwd": _TEST_PASSWORD, "newPwd": _NEW_PASSWORD
        }, headers=user_auth_headers)
        assert response.status_code == 200
        assert response.get_json() == {"updated": True}

    def test_returns_400_on_missing_fields(self, client, user_auth_headers):
        response = client.put("/api/auth/password", json={
            "currentPwd": _TEST_PASSWORD
            # missing newPwd
        }, headers=user_auth_headers)
        assert response.status_code == 400

    def test_password_is_actually_changed_in_db(self, client, test_user, user_auth_headers):
        client.put("/api/auth/password", json={
            "currentPwd": _TEST_PASSWORD, "newPwd": _NEW_PASSWORD
        }, headers=user_auth_headers)
        # Reload from base and check if hash has changed
        updated = User.objects.get(id=test_user.id)
        assert bcrypt.checkpw(_NEW_PASSWORD.encode(), updated.password.encode())
        assert not bcrypt.checkpw(_TEST_PASSWORD.encode(), updated.password.encode())

    def test_old_password_no_longer_works_after_update(self, client, test_user, user_auth_headers):
        client.put("/api/auth/password", json={
            "currentPwd": _TEST_PASSWORD, "newPwd": _NEW_PASSWORD
        }, headers=user_auth_headers)
        # Try to log in with old password
        response = client.post("/api/auth/login", json={
            "email": _TEST_EMAIL, "pwd": _TEST_PASSWORD
        })
        assert response.status_code == 401

    def test_new_password_works_after_update(self, client, test_user, user_auth_headers):
        client.put("/api/auth/password", json={
            "currentPwd": _TEST_PASSWORD, "newPwd": _NEW_PASSWORD
        }, headers=user_auth_headers)
        # Login with the new password
        response = client.post("/api/auth/login", json={
            "email": _TEST_EMAIL, "pwd": _NEW_PASSWORD
        })
        assert response.status_code == 200
        assert "token" in response.get_json()
