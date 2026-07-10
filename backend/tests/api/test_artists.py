import re
import pytest

from models.artist import Artist, Album, Track

_UUID4_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')

_VALID_TRACK = {"trackNumber": 1, "title": "Track 1", "src": "track.mp3", "tags": []}
_VALID_ALBUM = {"slug": "album-1", "title": "Album 1", "order": 1, "tracks": [_VALID_TRACK]}
_VALID_ARTIST_PAYLOAD = {"slug": "artist-1", "title": "Artist 1", "order": 1, "albums": [_VALID_ALBUM]}
_NONEXISTENT_ID = "000000000000000000000001"


@pytest.fixture
def test_artist(test_artist_user):
    return Artist(
        user=test_artist_user,
        slug="artist-1",
        title="Artist 1",
        order=1,
        albums=[Album(
            slug="album-1",
            title="Album 1",
            order=1,
            tracks=[Track(trackNumber=1, title="Track 1", src="track.mp3")]
        )]
    ).save()


class TestGetArtists:
    def test_returns_empty_list_when_no_artists(self, client):
        response = client.get("/api/artists")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_returns_artists(self, client, test_artist):
        response = client.get("/api/artists")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Artist 1"
        assert "_id" in data[0]


class TestUpdateArtists:
    def test_requires_authentication(self, client):
        response = client.put("/api/artists", json=[_VALID_ARTIST_PAYLOAD])
        assert response.status_code == 401

    def test_requires_json_content_type(self, client, auth_headers):
        response = client.put("/api/artists", data="raw", content_type="text/plain",
                              headers=auth_headers)
        assert response.status_code == 415

    def test_returns_400_when_payload_is_not_a_list(self, client, auth_headers):
        response = client.put("/api/artists", json=_VALID_ARTIST_PAYLOAD,
                              headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Expected a list of artists"}

    def test_returns_400_on_invalid_payload(self, client, auth_headers):
        response = client.put("/api/artists", json=[{"title": "Missing required fields"}],
                              headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Invalid payload"}

    def test_returns_400_on_mongoengine_validation_error(self, client, auth_headers):
        # Empty albums passes Pydantic but fails Artist.clean()
        response = client.put("/api/artists", json=[{**_VALID_ARTIST_PAYLOAD, "albums": []}],
                              headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "invalid data"}

    def test_returns_404_when_artist_not_found(self, client, auth_headers):
        response = client.put("/api/artists",
                              json=[{**_VALID_ARTIST_PAYLOAD, "_id": _NONEXISTENT_ID}],
                              headers=auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "Artist not found"}

    def test_creates_new_artist(self, client, auth_headers):
        response = client.put("/api/artists", json=[_VALID_ARTIST_PAYLOAD],
                              headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["title"] == "Artist 1"
        assert data[0]["_id"]
        assert _UUID4_RE.match(data[0]["slug"])
        assert _UUID4_RE.match(data[0]["albums"][0]["slug"])
        track_src = data[0]["albums"][0]["tracks"][0]["src"]
        assert _UUID4_RE.match(track_src.removesuffix(".mp3"))
        assert Artist.objects.count() == 1

    def test_updates_existing_artist(self, client, auth_headers, test_artist):
        payload = {**_VALID_ARTIST_PAYLOAD, "_id": str(test_artist.id), "title": "Updated Artist"}
        response = client.put("/api/artists", json=[payload], headers=auth_headers)
        assert response.status_code == 200
        assert Artist.objects.get(id=test_artist.id).title == "Updated Artist"


class TestDeleteArtist:
    def test_requires_authentication(self, client):
        response = client.delete(f"/api/artists/{_NONEXISTENT_ID}")
        assert response.status_code == 401

    def test_returns_400_on_invalid_id_format(self, client, auth_headers):
        response = client.delete("/api/artists/not-valid", headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Invalid ID"}

    def test_returns_404_when_artist_not_found(self, client, auth_headers):
        response = client.delete(f"/api/artists/{_NONEXISTENT_ID}", headers=auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "Artist not found"}

    def test_deletes_artist(self, client, auth_headers, test_artist):
        response = client.delete(f"/api/artists/{test_artist.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == {"deleted": True}
        assert Artist.objects.count() == 0
