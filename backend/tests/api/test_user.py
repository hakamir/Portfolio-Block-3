from models.user import User

_NONEXISTENT_ID = "000000000000000000000001"
_INVALID_ID = "not-a-valid-id"
_VALID_PASSWORD = "password1234567"


class TestGetUsers:
    def test_requires_authentication(self, client):
        response = client.get("/api/users")
        assert response.status_code == 401

    def test_requires_admin_role(self, client, auth_headers):
        response = client.get("/api/users", headers=auth_headers)
        assert response.status_code == 403

    def test_returns_all_users(self, client, admin_auth_headers, test_artist_user, test_admin_user):
        response = client.get("/api/users", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_user_fields_do_not_expose_password(self, client, admin_auth_headers, test_artist_user):
        response = client.get("/api/users", headers=admin_auth_headers)
        assert response.status_code == 200
        user = response.get_json()[0]
        assert "password" not in user
        assert "id" in user
        assert "email" in user
        assert "role" in user
        assert "is_active" in user


class TestGetUserById:
    def test_requires_authentication(self, client, test_artist_user):
        response = client.get(f"/api/users/{test_artist_user.id}")
        assert response.status_code == 401

    def test_requires_admin_role(self, client, auth_headers, test_artist_user):
        response = client.get(f"/api/users/{test_artist_user.id}", headers=auth_headers)
        assert response.status_code == 403

    def test_returns_400_on_invalid_id_format(self, client, admin_auth_headers):
        response = client.get(f"/api/users/{_INVALID_ID}", headers=admin_auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Invalid ID"}

    def test_returns_404_when_user_not_found(self, client, admin_auth_headers):
        response = client.get(f"/api/users/{_NONEXISTENT_ID}", headers=admin_auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "User not found"}

    def test_returns_user(self, client, admin_auth_headers, test_artist_user):
        response = client.get(f"/api/users/{test_artist_user.id}", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == str(test_artist_user.id)
        assert data["email"] == test_artist_user.email
        assert "password" not in data


class TestCreateUser:
    def test_requires_authentication(self, client):
        response = client.post("/api/users", json={})
        assert response.status_code == 401

    def test_requires_admin_role(self, client, auth_headers):
        response = client.post("/api/users", json={}, headers=auth_headers)
        assert response.status_code == 403

    def test_returns_400_when_password_too_short(self, client, admin_auth_headers):
        response = client.post("/api/users", json={
            "email": "new@test.com",
            "password": "short"
        }, headers=admin_auth_headers)
        assert response.status_code == 400

    def test_creates_user(self, client, admin_auth_headers):
        response = client.post("/api/users", json={
            "email": "new@test.com",
            "password": _VALID_PASSWORD,
            "role": "artist"
        }, headers=admin_auth_headers)
        assert response.status_code == 201
        assert response.get_json() == {"created": True}
        assert User.objects(email="new@test.com").first() is not None

    def test_creates_user_with_default_role(self, client, admin_auth_headers):
        response = client.post("/api/users", json={
            "email": "new@test.com",
            "password": _VALID_PASSWORD
        }, headers=admin_auth_headers)
        assert response.status_code == 201
        assert User.objects(email="new@test.com").first().role == "artist"


class TestDeleteUser:
    def test_requires_authentication(self, client, test_artist_user):
        response = client.delete(f"/api/users/{test_artist_user.id}")
        assert response.status_code == 401

    def test_requires_admin_role(self, client, auth_headers, test_artist_user):
        response = client.delete(f"/api/users/{test_artist_user.id}", headers=auth_headers)
        assert response.status_code == 403

    def test_returns_400_on_invalid_id_format(self, client, admin_auth_headers):
        response = client.delete(f"/api/users/{_INVALID_ID}", headers=admin_auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Invalid ID"}

    def test_returns_400_when_deleting_own_account(self, client, admin_auth_headers, test_admin_user):
        response = client.delete(f"/api/users/{test_admin_user.id}", headers=admin_auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Cannot delete own account"}

    def test_returns_400_when_user_is_active(self, client, admin_auth_headers, test_artist_user):
        response = client.delete(f"/api/users/{test_artist_user.id}", headers=admin_auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Cannot delete active user"}

    def test_deletes_inactive_user(self, client, admin_auth_headers):
        inactive = User(
            email="inactive@test.com",
            password="hashed",
            role="artist",
            is_active=False
        ).save()

        response = client.delete(f"/api/users/{inactive.id}", headers=admin_auth_headers)

        assert response.status_code == 204
        assert User.objects(id=inactive.id).first() is None


class TestUpdateRole:
    def test_requires_authentication(self, client, test_artist_user):
        response = client.put(f"/api/users/{test_artist_user.id}/role", json={"role": "admin"})
        assert response.status_code == 401

    def test_requires_admin_role(self, client, auth_headers, test_artist_user):
        response = client.put(f"/api/users/{test_artist_user.id}/role", json={"role": "admin"},
                              headers=auth_headers)
        assert response.status_code == 403

    def test_returns_400_when_updating_own_role(self, client, admin_auth_headers, test_admin_user):
        response = client.put(f"/api/users/{test_admin_user.id}/role", json={"role": "artist"},
                              headers=admin_auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Cannot update own role"}

    def test_returns_400_on_invalid_id_format(self, client, admin_auth_headers):
        response = client.put(f"/api/users/{_INVALID_ID}/role", json={"role": "artist"},
                              headers=admin_auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Invalid ID"}

    def test_returns_400_on_invalid_role(self, client, admin_auth_headers, test_artist_user):
        inactive = User(
            email="inactive@test.com",
            password="hashed",
            role="artist",
            is_active=False
        ).save()
        response = client.put(f"/api/users/{inactive.id}/role", json={"role": "superuser"},
                              headers=admin_auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Invalid role"}

    def test_returns_400_when_updating_role_of_active_user(self, client, admin_auth_headers, test_artist_user):
        response = client.put(f"/api/users/{test_artist_user.id}/role", json={"role": "admin"},
                              headers=admin_auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Cannot update role of active user"}

    def test_updates_role(self, client, admin_auth_headers):
        inactive_artist = User(
            email="inactive@test.com",
            password="hashed",
            role="artist",
            is_active=False
        ).save()

        response = client.put(f"/api/users/{inactive_artist.id}/role", json={"role": "admin"},
                              headers=admin_auth_headers)

        assert response.status_code == 200
        assert response.get_json() == {"updated": True}
        assert User.objects.get(id=inactive_artist.id).role == "admin"


class TestActivateUser:
    def test_requires_authentication(self, client, test_artist_user):
        response = client.put(f"/api/users/{test_artist_user.id}/activate")
        assert response.status_code == 401

    def test_requires_admin_role(self, client, auth_headers, test_artist_user):
        response = client.put(f"/api/users/{test_artist_user.id}/activate", headers=auth_headers)
        assert response.status_code == 403

    def test_returns_400_on_invalid_id_format(self, client, admin_auth_headers):
        response = client.put(f"/api/users/{_INVALID_ID}/activate", headers=admin_auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Invalid ID"}

    def test_returns_404_when_user_not_found(self, client, admin_auth_headers):
        response = client.put(f"/api/users/{_NONEXISTENT_ID}/activate", headers=admin_auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "User not found"}

    def test_returns_404_when_user_is_not_artist(self, client, admin_auth_headers, test_admin_user):
        response = client.put(f"/api/users/{test_admin_user.id}/activate", headers=admin_auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "User not found"}

    def test_activates_artist(self, client, admin_auth_headers):
        artist = User(
            email="inactive@test.com",
            password="hashed",
            role="artist",
            is_active=False
        ).save()

        response = client.put(f"/api/users/{artist.id}/activate", headers=admin_auth_headers)

        assert response.status_code == 200
        assert response.get_json() == {"activated": True}
        assert User.objects.get(id=artist.id).is_active is True

    def test_deactivates_previously_active_artist(self, client, admin_auth_headers, test_artist_user):
        other = User(
            email="other@test.com",
            password="hashed",
            role="artist",
            is_active=False
        ).save()

        client.put(f"/api/users/{other.id}/activate", headers=admin_auth_headers)

        assert User.objects.get(id=test_artist_user.id).is_active is False
        assert User.objects.get(id=other.id).is_active is True
