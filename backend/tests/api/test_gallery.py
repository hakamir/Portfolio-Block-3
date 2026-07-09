import pytest
from datetime import datetime, timezone

from models.gallery import Gallery, GalleryImage

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


class TestGetGallery:
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

    def test_returns_400_when_image_slug_mismatches_gallery_slug(self, client, auth_headers):
        # src slug is "other-gallery" but gallery slug is "gallery-1"
        mismatched_image = {**_VALID_IMAGE,
                            "src": "other-gallery_a296a2f6-5ff9-4e49-bd5a-23d16b34b863.webp"}
        response = client.put("/api/gallery",
                              json=[{**_VALID_GALLERY_PAYLOAD, "images": [mismatched_image]}],
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
        assert response.get_json() == {"updated": True}
        assert Gallery.objects.count() == 1

    def test_updates_existing_gallery(self, client, auth_headers, test_gallery):
        payload = {**_VALID_GALLERY_PAYLOAD, "_id": str(test_gallery.id), "title": "Updated Gallery"}
        response = client.put("/api/gallery", json=[payload], headers=auth_headers)
        assert response.status_code == 200
        assert Gallery.objects.get(id=test_gallery.id).title == "Updated Gallery"


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
