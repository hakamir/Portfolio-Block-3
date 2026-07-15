import re

import pytest
from datetime import datetime, timezone

from models.gallery import Gallery, GalleryImage
from models.user import User

_UUID4_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')

_VALID_IMAGE = {
    "src": "gallery-1_a296a2f6-5ff9-4e49-bd5a-23d16b34b863.webp",
    "title": "Image 1",
    "location": "Paris",
    "date": "2024-01-01T00:00:00",
    "order": 1,
    "alt": "Image 1, Paris, 2024"
}
_VALID_GALLERY_PAYLOAD = {
    "slug": "gallery-1",
    "title": "Gallery 1",
    "order": 1,
    "images": [_VALID_IMAGE]
}
_NONEXISTENT_ID = "000000000000000000000001"


@pytest.fixture
def test_gallery(test_artist_user):
    return Gallery(
        slug="gallery-1",
        title="Gallery 1",
        order=1,
        user=test_artist_user,
        images=[GalleryImage(
            src="gallery-1_a296a2f6-5ff9-4e49-bd5a-23d16b34b863.webp",
            title="Image 1",
            location="Paris",
            date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            order=1,
            alt="Image 1, Paris, 2024"
        )]
    ).save()


class TestGetActiveGallery:
    def test_returns_empty_list_when_no_galleries(self, client):
        response = client.get("/api/gallery")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_returns_galleries(self, client, test_gallery):
        response = client.get("/api/gallery")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Gallery 1"
        assert "_id" in data[0]

    def test_returns_empty_list_when_no_active_artist(self, client, test_artist_user):
        test_artist_user.is_active = False
        test_artist_user.save()
        response = client.get("/api/gallery")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_does_not_return_inactive_artist_galleries(self, client, test_artist_user):
        other = User(email="other@test.com", password="x", role="artist", is_active=False).save()
        Gallery(
            user=other, slug="other-gallery", title="Other Gallery", order=1, images=[]
        ).save()
        Gallery(
            user=test_artist_user, slug="active-gallery", title="Active Gallery", order=1, images=[]
        ).save()
        response = client.get("/api/gallery")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Active Gallery"

    def test_user_field_not_exposed(self, client, test_gallery):
        response = client.get("/api/gallery")
        assert response.status_code == 200
        assert "user" not in response.get_json()[0]


class TestGetOwnedGalleries:
    def test_requires_authentication(self, client):
        response = client.get("/api/gallery/dashboard")
        assert response.status_code == 401

    def test_returns_empty_list_when_no_galleries(self, client, auth_headers):
        response = client.get("/api/gallery/dashboard", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == []

    def test_returns_owned_galleries_only(self, client, auth_headers, test_artist_user):
        Gallery(
            user=test_artist_user, slug="mine", title="Mine", order=1, images=[]
        ).save()
        other = User(email="other@test.com", password="x", role="artist", is_active=False).save()
        Gallery(
            user=other, slug="theirs", title="Theirs", order=1, images=[]
        ).save()

        response = client.get("/api/gallery/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Mine"

    def test_user_field_not_exposed(self, client, auth_headers, test_artist_user):
        Gallery(
            user=test_artist_user, slug="mine", title="Mine", order=1, images=[]
        ).save()
        response = client.get("/api/gallery/dashboard", headers=auth_headers)
        assert "user" not in response.get_json()[0]


class TestGetGalleryByUserId:
    def test_requires_authentication(self, client, test_artist_user):
        response = client.get(f"/api/gallery/{test_artist_user.id}")
        assert response.status_code == 401

    def test_requires_admin_role(self, client, auth_headers, test_artist_user):
        response = client.get(f"/api/gallery/{test_artist_user.id}", headers=auth_headers)
        assert response.status_code == 403

    def test_returns_400_on_invalid_id(self, client, admin_auth_headers):
        response = client.get("/api/gallery/not-valid", headers=admin_auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Invalid ID"}

    def test_returns_404_when_user_not_found(self, client, admin_auth_headers):
        response = client.get(f"/api/gallery/{_NONEXISTENT_ID}", headers=admin_auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "user not found"}

    def test_returns_empty_list_when_user_has_no_galleries(self, client, admin_auth_headers, test_artist_user):
        response = client.get(f"/api/gallery/{test_artist_user.id}", headers=admin_auth_headers)
        assert response.status_code == 200
        assert response.get_json() == []

    def test_returns_galleries_for_user(self, client, admin_auth_headers, test_gallery, test_artist_user):
        response = client.get(f"/api/gallery/{test_artist_user.id}", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Gallery 1"


class TestUpdateGalleries:
    def test_requires_authentication(self, client):
        response = client.put("/api/gallery", json=[_VALID_GALLERY_PAYLOAD])
        assert response.status_code == 401

    def test_requires_json_content_type(self, client, auth_headers):
        response = client.put("/api/gallery", data="raw", content_type="text/plain",
                              headers=auth_headers)
        assert response.status_code == 415

    def test_returns_400_when_payload_is_not_a_list(self, client, auth_headers):
        response = client.put("/api/gallery", json=_VALID_GALLERY_PAYLOAD,
                              headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Expected a list of galleries"}

    def test_returns_400_on_invalid_payload(self, client, auth_headers):
        # Missing required fields
        response = client.put("/api/gallery", json=[{"title": "Missing fields"}],
                              headers=auth_headers)
        assert response.status_code == 400

    def test_returns_404_when_gallery_not_found(self, client, auth_headers):
        response = client.put("/api/gallery",
                              json=[{**_VALID_GALLERY_PAYLOAD, "_id": _NONEXISTENT_ID}],
                              headers=auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "Gallery not found"}

    def test_creates_new_gallery(self, client, auth_headers):
        response = client.put("/api/gallery", json=[_VALID_GALLERY_PAYLOAD],
                              headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["title"] == "Gallery 1"
        assert data[0]["_id"]
        assert _UUID4_RE.match(data[0]["slug"])
        image_src = data[0]["images"][0]["src"]
        assert _UUID4_RE.match(image_src.removesuffix(".webp"))
        assert Gallery.objects.count() == 1

    def test_updates_existing_gallery(self, client, auth_headers, test_gallery):
        payload = {**_VALID_GALLERY_PAYLOAD, "_id": str(test_gallery.id), "title": "Updated Gallery"}
        response = client.put("/api/gallery", json=[payload], headers=auth_headers)
        assert response.status_code == 200
        assert Gallery.objects.get(id=test_gallery.id).title == "Updated Gallery"

    def test_artist_cannot_update_other_artist_gallery(self, client, auth_headers):
        other = User(email="other@test.com", password="x", role="artist", is_active=False).save()
        other_gallery = Gallery(
            user=other, slug="other", title="Other", order=1, images=[]
        ).save()
        payload = [{**_VALID_GALLERY_PAYLOAD, "_id": str(other_gallery.id)}]
        response = client.put("/api/gallery", json=payload, headers=auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "Gallery not found"}

    def test_returns_gallery_data_in_response(self, client, auth_headers):
        response = client.put("/api/gallery", json=[_VALID_GALLERY_PAYLOAD], headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert data[0]["title"] == "Gallery 1"
        assert "user" not in data[0]


class TestDeleteGallery:
    def test_requires_authentication(self, client):
        response = client.delete(f"/api/gallery/{_NONEXISTENT_ID}")
        assert response.status_code == 401

    def test_returns_400_on_invalid_id_format(self, client, auth_headers):
        response = client.delete("/api/gallery/not-valid", headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Invalid ID"}

    def test_returns_404_when_gallery_not_found(self, client, auth_headers):
        response = client.delete(f"/api/gallery/{_NONEXISTENT_ID}", headers=auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "Gallery not found"}

    def test_deletes_gallery(self, client, auth_headers, test_gallery):
        response = client.delete(f"/api/gallery/{test_gallery.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == {"deleted": True}
        assert Gallery.objects.count() == 0

    def test_artist_cannot_delete_other_artist_gallery(self, client, auth_headers):
        other = User(email="other@test.com", password="x", role="artist", is_active=False).save()
        other_gallery = Gallery(
            user=other, slug="other", title="Other", order=1, images=[]
        ).save()
        response = client.delete(f"/api/gallery/{other_gallery.id}", headers=auth_headers)
        assert response.status_code == 404
        assert Gallery.objects.count() == 1
