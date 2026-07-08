from urllib import response

from models.biography import Biography, Section
from models.user import User

_VALID_SECTIONS = [{"title": "Section", "paragraphs": ["Para"]}]
_NONEXISTENT_ID = "000000000000000000000001"


class TestGetBiography:
    def test_returns_404_when_no_biography(self, client):
        response = client.get("/api/biography")
        assert response.status_code == 404
        assert response.get_json() == {"error": "biography not found"}

    def test_returns_biography(self, client, test_artist_user):
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


class TestUpdateBiography:
    def test_requires_authentication(self, client):
        response = client.put("/api/biography", json={
            "_id": _NONEXISTENT_ID,
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

    def test_returns_400_on_invalid_id_format(self, client, auth_headers):
        response = client.put("/api/biography", json={
            "_id": "not-a-valid-id",
            "title": "T",
            "sections": _VALID_SECTIONS
        }, headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "invalid ID"}

    def test_returns_404_when_biography_not_found(self, client, auth_headers):
        response = client.put("/api/biography", json={
            "_id": _NONEXISTENT_ID,
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
            "_id": str(bio.id),
            "title": "Updated Title",
            "sections": [{"title": "New Section", "paragraphs": ["New para"]}]
        }, headers=auth_headers)

        assert response.status_code == 200
        assert response.get_json() == {"updated": True}
        assert Biography.objects.get(id=bio.id).title == "Updated Title"

    def test_artist_cannot_update_other_artist_biography(self, client, auth_headers):
        # Create a second artist with his own biography
        other_artist = User(
            email="other@test.com",
            password="hashed",
            role="artist",
            is_active=False
        ).save()
        bio = Biography(
            user=other_artist,
            title="Other Artist Bio",
            sections=[]
        ).save()

        # First artist (test_artist_user) try to modify the biography of the second artist
        response = client.put("/api/biography", json={
            "_id": str(bio.id),
            "title": "Hacked Title",
            "sections": []
        }, headers=auth_headers)

        assert response.status_code == 404
        assert Biography.objects.get(id=bio.id).title == "Other Artist Bio"


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