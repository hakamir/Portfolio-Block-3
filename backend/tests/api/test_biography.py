import pytest
from models.biography import Biography, Section
from models.user import User

_VALID_SECTIONS = [{"title": "Section", "paragraphs": ["Para"]}]
_NONEXISTENT_ID = "000000000000000000000001"


@pytest.fixture
def inactive_artist_user(app):
    with app.app_context():
        return User(
            email="inactive_artist@test.com",
            password="hashed_password",
            role="artist",
            is_active=False
        ).save()


class TestGetActiveBiography:
    def test_returns_404_when_no_active_biography(self, client):
        response = client.get("/api/biography")
        assert response.status_code == 404
        assert response.get_json() == {"error": "biography not found"}

    def test_returns_active_biography(self, client, test_artist_user):
        Biography(
            user=test_artist_user,
            title="Test Biography",
            sections=[Section(title="Section 1", paragraphs=["Paragraph 1"])]
        ).save()

        response = client.get("/api/biography")

        assert response.status_code == 200
        data = response.get_json()
        assert "biography" in data
        assert data["biography"]["title"] == "Test Biography"
        assert "_id" in data["biography"]
        assert "user" not in data["biography"]

    def test_returns_404_when_no_active_user(self, client):
        response = client.get("/api/biography")
        assert response.status_code == 404
        assert response.get_json() == {"error": "biography not found"}

    def test_does_not_return_inactive_artist_biography(self, client, inactive_artist_user):
        Biography(
            user=inactive_artist_user,
            title="Inactive",
            sections=[]
        ).save()
        response = client.get("/api/biography")
        assert response.status_code == 404


class TestUpdateBiography:
    def test_requires_authentication(self, client):
        response = client.put("/api/biography", json={
            "title": "T",
            "sections": _VALID_SECTIONS
        })
        assert response.status_code == 401

    def test_requires_json_content_type(self, client, auth_headers):
        response = client.put("/api/biography", data="raw", content_type="text/plain",
                              headers=auth_headers)
        assert response.status_code == 415
        assert response.get_json() == {"error": "invalid content-type"}

    def test_returns_400_on_invalid_payload(self, client, auth_headers):
        response = client.put("/api/biography", json={"title": "Missing fields"},
                              headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "invalid payload"}

    def test_returns_400_when_id_present_in_body(self, client, auth_headers):
        response = client.put("/api/biography", json={
            "_id": _NONEXISTENT_ID,
            "title": "T",
            "sections": _VALID_SECTIONS
        }, headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "invalid payload"}

    def test_returns_404_when_biography_not_found(self, client, auth_headers):
        # test_artist_user has no biography yet
        response = client.put("/api/biography", json={
            "title": "T",
            "sections": _VALID_SECTIONS
        }, headers=auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "biography not found"}

    def test_updates_biography(self, client, auth_headers, test_artist_user):
        bio = Biography(
            user=test_artist_user,
            title="Original",
            sections=[]
        ).save()

        response = client.put("/api/biography", json={
            "title": "Updated Title",
            "sections": [{"title": "New Section", "paragraphs": ["New para"]}]
        }, headers=auth_headers)

        assert response.status_code == 200
        assert response.get_json() == {"updated": True}
        assert Biography.objects.get(id=bio.id).title == "Updated Title"

    def test_update_only_affects_own_biography(self, client, auth_headers, test_artist_user):
        # Create a second artist with his own biography
        other_artist = User(
            email="other@test.com",
            password="hashed",
            role="artist",
            is_active=False
        ).save()
        other_bio = Biography(
            user=other_artist,
            title="Other Artist Bio",
            sections=[]
        ).save()

        own_bio = Biography(
            user=test_artist_user,
            title="My Bio",
            sections=[]
        ).save()

        # test_artist_user can only ever update their own biography,
        # regardless of what's sent — there's no way to target another user's
        response = client.put("/api/biography", json={
            "title": "Updated Title",
            "sections": []
        }, headers=auth_headers)

        assert response.status_code == 200
        assert Biography.objects.get(id=own_bio.id).title == "Updated Title"
        assert Biography.objects.get(id=other_bio.id).title == "Other Artist Bio"


class TestCreateBiography:
    def test_requires_authentication(self, client):
        response = client.post("/api/biography", json={})
        assert response.status_code == 401

    def test_requires_admin_role(self, client, auth_headers):
        response = client.post("/api/biography", json={}, headers=auth_headers)
        assert response.status_code == 403

    def test_requires_json_content_type(self, client, admin_auth_headers):
        response = client.post("/api/biography", data="raw", content_type="text/plain",
                               headers=admin_auth_headers)
        assert response.status_code == 415
        assert response.get_json() == {"error": "invalid content-type"}

    def test_returns_400_on_invalid_payload(self, client, admin_auth_headers):
        response = client.post("/api/biography", json={"title": "Missing fields"},
                               headers=admin_auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "invalid payload"}

    def test_returns_404_when_artist_not_found(self, client, admin_auth_headers):
        response = client.post("/api/biography", json={
            "title": "Test Biography",
            "sections": _VALID_SECTIONS,
            "user_id": _NONEXISTENT_ID
        }, headers=admin_auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "user not found"}

    def test_returns_409_when_biography_already_exists(self, client, admin_auth_headers, test_artist_user):
        Biography(
            user=test_artist_user,
            title="Existing Bio",
            sections=[]
        ).save()
        response = client.post("/api/biography", json={
            "title": "New Bio",
            "sections": _VALID_SECTIONS,
            "user_id": str(test_artist_user.id)
        }, headers=admin_auth_headers)
        assert response.status_code == 409
        assert response.get_json() == {"error": "biography already exists"}

    def test_creates_biography(self, client, admin_auth_headers, test_artist_user):
        response = client.post("/api/biography", json={
            "title": "New Biography",
            "sections": _VALID_SECTIONS,
            "user_id": str(test_artist_user.id)
        }, headers=admin_auth_headers)
        assert response.status_code == 201
        assert response.get_json() == {"created": True}
        assert Biography.objects(user=test_artist_user).first() is not None
        assert Biography.objects(user=test_artist_user).first().title == "New Biography"

    def test_returns_404_when_user_id_is_not_an_artist(self, client, admin_auth_headers, test_admin_user):
        response = client.post("/api/biography", json={
            "title": "New Biography",
            "sections": _VALID_SECTIONS,
            "user_id": str(test_admin_user.id)
        }, headers=admin_auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "user not found"}


class TestGetDashboardBiography:
    def test_requires_authentication(self, client):
        response = client.get("/api/biography/dashboard")
        assert response.status_code == 401

    def test_returns_404_when_no_biography(self, client, auth_headers):
        response = client.get("/api/biography/dashboard", headers=auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "biography not found"}

    def test_artist_returns_own_biography(self, client, auth_headers, test_artist_user):
        Biography(
            user=test_artist_user,
            title="Artist Bio",
            sections=[Section(title="Section 1", paragraphs=["Para 1"])]
        ).save()

        response = client.get("/api/biography/dashboard", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert "biography" in data
        assert data["biography"]["title"] == "Artist Bio"
        assert "_id" in data["biography"]
        assert "user" not in data["biography"]

    def test_admin_returns_own_biography(self, client, admin_auth_headers, test_admin_user):
        Biography(
            user=test_admin_user,
            title="Admin Bio",
            sections=[]
        ).save()

        response = client.get("/api/biography/dashboard", headers=admin_auth_headers)

        assert response.status_code == 200
        assert response.get_json()["biography"]["title"] == "Admin Bio"

    def test_does_not_return_other_user_biography(self, client, auth_headers):
        other_artist = User(
            email="other@test.com",
            password="hashed",
            role="artist",
            is_active=False
        ).save()
        Biography(user=other_artist, title="Other Bio", sections=[]).save()

        response = client.get("/api/biography/dashboard", headers=auth_headers)

        assert response.status_code == 404


class TestGetBiographyByUserId:
    def test_requires_authentication(self, client, test_artist_user):
        response = client.get(f"/api/biography/{test_artist_user.id}")
        assert response.status_code == 401

    def test_requires_admin_role(self, client, auth_headers, test_artist_user):
        response = client.get(f"/api/biography/{test_artist_user.id}", headers=auth_headers)
        assert response.status_code == 403

    def test_returns_404_when_user_not_found(self, client, admin_auth_headers):
        response = client.get(f"/api/biography/{_NONEXISTENT_ID}", headers=admin_auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "user not found"}

    def test_returns_404_when_biography_not_found(self, client, admin_auth_headers, test_artist_user):
        response = client.get(f"/api/biography/{test_artist_user.id}", headers=admin_auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "biography not found"}

    def test_returns_biography(self, client, admin_auth_headers, test_artist_user):
        Biography(
            user=test_artist_user,
            title="Artist Bio",
            sections=[Section(title="S", paragraphs=["P"])]
        ).save()

        response = client.get(f"/api/biography/{test_artist_user.id}", headers=admin_auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert "biography" in data
        assert data["biography"]["title"] == "Artist Bio"
        assert "user" not in data["biography"]


class TestDeleteBiography:
    def test_requires_authentication(self, client, test_artist_user):
        response = client.delete(f"/api/biography/{test_artist_user.id}")
        assert response.status_code == 401

    def test_requires_admin_role(self, client, auth_headers, test_artist_user):
        response = client.delete(f"/api/biography/{test_artist_user.id}", headers=auth_headers)
        assert response.status_code == 403

    def test_returns_404_when_user_not_found(self, client, admin_auth_headers):
        response = client.delete(f"/api/biography/{_NONEXISTENT_ID}", headers=admin_auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "user not found"}

    def test_returns_404_when_biography_not_found(self, client, admin_auth_headers, inactive_artist_user):
        response = client.delete(f"/api/biography/{inactive_artist_user.id}", headers=admin_auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "biography not found"}

    def test_deletes_biography(self, client, admin_auth_headers, inactive_artist_user):
        Biography(user=inactive_artist_user, title="To Delete", sections=[]).save()

        response = client.delete(f"/api/biography/{inactive_artist_user.id}", headers=admin_auth_headers)

        assert response.status_code == 204
        assert Biography.objects(user=inactive_artist_user).first() is None

    def test_returns_400_on_invalid_id_format(self, client, admin_auth_headers):
        response = client.delete("/api/biography/not-valid", headers=admin_auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Invalid ID"}

    def test_cannot_delete_biography_of_active_user(self, client, admin_auth_headers, test_artist_user):
        Biography(
            user=test_artist_user,
            title="Active Bio",
            sections=[]
        ).save()
        # test_artist_user is active
        response = client.delete(f"/api/biography/{test_artist_user.id}", headers=admin_auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Cannot delete biography of an active user"}
        # Biography must not have been deleted
        assert Biography.objects(user=test_artist_user).first() is not None
