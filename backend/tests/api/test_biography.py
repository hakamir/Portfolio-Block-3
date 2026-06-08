from models.biography import Biography, ImageSize, Section

_VALID_IMAGE = {"sm": "/bio-512.webp", "md": "/bio-1024.webp", "lg": "/bio-2048.webp"}
_VALID_SECTIONS = [{"title": "Section", "paragraphs": ["Para"]}]
_NONEXISTENT_ID = "000000000000000000000001"


class TestGetBiography:
    def test_returns_404_when_no_biography(self, client):
        response = client.get("/api/biography")
        assert response.status_code == 404
        assert response.get_json() == {"error": "biography not found"}

    def test_returns_biography(self, client):
        Biography(
            title="Test Biography",
            image=ImageSize(sm="/bio-512.webp", md="/bio-1024.webp", lg="/bio-2048.webp"),
            sections=[Section(title="Section 1", paragraphs=["Paragraph 1"])]
        ).save()

        response = client.get("/api/biography")

        assert response.status_code == 200
        data = response.get_json()
        assert "biography" in data
        assert data["biography"]["title"] == "Test Biography"
        assert "_id" in data["biography"]


class TestUpdateBiography:
    def test_requires_authentication(self, client):
        response = client.put("/api/biography", json={
            "_id": _NONEXISTENT_ID, "title": "T", "image": _VALID_IMAGE, "sections": _VALID_SECTIONS
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
            "_id": "not-a-valid-id", "title": "T", "image": _VALID_IMAGE, "sections": _VALID_SECTIONS
        }, headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "invalid ID"}

    def test_returns_404_when_biography_not_found(self, client, auth_headers):
        response = client.put("/api/biography", json={
            "_id": _NONEXISTENT_ID, "title": "T", "image": _VALID_IMAGE, "sections": _VALID_SECTIONS
        }, headers=auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "biography not found"}

    def test_updates_biography(self, client, auth_headers):
        bio = Biography(
            title="Original",
            image=ImageSize(sm="/bio-512.webp", md="/bio-1024.webp", lg="/bio-2048.webp"),
            sections=[]
        ).save()

        response = client.put("/api/biography", json={
            "_id": str(bio.id),
            "title": "Updated Title",
            "image": _VALID_IMAGE,
            "sections": [{"title": "New Section", "paragraphs": ["New para"]}]
        }, headers=auth_headers)

        assert response.status_code == 200
        assert response.get_json() == {"updated": True}
        assert Biography.objects.get(id=bio.id).title == "Updated Title"
