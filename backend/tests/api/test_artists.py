import re
import pytest

from models.artist import Artist, Album, Track
from models.user import User

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


class TestGetActiveArtists:
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

    def test_returns_empty_list_when_no_active_artist(self, client, test_artist_user):
        test_artist_user.is_active = False
        test_artist_user.save()
        Artist(
            user=test_artist_user,
            slug="artist-1",
            title="Artist 1",
            order=1,
            albums=[Album(slug="a", title="A", order=1, tracks=[Track(trackNumber=1, title="T", src="t.mp3")])]
        ).save()
        response = client.get("/api/artists")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_does_not_return_inactive_artist_data(self, client, test_artist_user):
        other = User(email="other@test.com", password="x", role="artist", is_active=False).save()
        Artist(
            user=other, slug="other-1", title="Other Artist", order=1,
            albums=[Album(slug="a", title="A", order=1, tracks=[Track(trackNumber=1, title="T", src="t.mp3")])]
        ).save()
        Artist(
            user=test_artist_user, slug="active-1", title="Active Artist", order=1,
            albums=[Album(slug="b", title="B", order=1, tracks=[Track(trackNumber=1, title="T", src="t.mp3")])]
        ).save()
        response = client.get("/api/artists")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Active Artist"

    def test_user_field_not_exposed(self, client, test_artist):
        response = client.get("/api/artists")
        assert response.status_code == 200
        assert "user" not in response.get_json()[0]


class TestGetOwnedArtists:
    def test_requires_authentication(self, client):
        response = client.get("/api/artists/dashboard")
        assert response.status_code == 401

    def test_returns_empty_list_when_no_artists(self, client, auth_headers):
        response = client.get("/api/artists/dashboard", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == []

    def test_returns_owned_artists_only(self, client, auth_headers, test_artist_user):
        # User connected to an artist document
        Artist(
            user=test_artist_user, slug="mine", title="Mine", order=1,
            albums=[Album(slug="a", title="A", order=1, tracks=[Track(trackNumber=1, title="T", src="t.mp3")])]
        ).save()
        # Second user connected to his owned document
        other = User(email="other@test.com", password="x", role="artist", is_active=False).save()
        Artist(
            user=other, slug="theirs", title="Theirs", order=1,
            albums=[Album(slug="b", title="B", order=1, tracks=[Track(trackNumber=1, title="T", src="t.mp3")])]
        ).save()

        response = client.get("/api/artists/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Mine"


class TestGetArtistByUserId:
    def test_requires_authentication(self, client, test_artist_user):
        response = client.get(f"/api/artists/{test_artist_user.id}")
        assert response.status_code == 401

    def test_requires_admin_role(self, client, auth_headers, test_artist_user):
        response = client.get(f"/api/artists/{test_artist_user.id}", headers=auth_headers)
        assert response.status_code == 403

    def test_returns_400_on_invalid_id(self, client, admin_auth_headers):
        response = client.get("/api/artists/not-valid", headers=admin_auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Invalid ID"}

    def test_returns_404_when_user_not_found(self, client, admin_auth_headers):
        response = client.get(f"/api/artists/{_NONEXISTENT_ID}", headers=admin_auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "user not found"}

    def test_returns_empty_list_when_user_has_no_artists(self, client, admin_auth_headers, test_artist_user):
        response = client.get(f"/api/artists/{test_artist_user.id}", headers=admin_auth_headers)
        assert response.status_code == 200
        assert response.get_json() == []

    def test_returns_artists_for_user(self, client, admin_auth_headers, test_artist, test_artist_user):
        response = client.get(f"/api/artists/{test_artist_user.id}", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Artist 1"


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

    def test_artist_cannot_update_other_artist_document(self, client, auth_headers):
        other = User(email="other@test.com", password="x", role="artist", is_active=False).save()
        other_artist = Artist(
            user=other, slug="other", title="Other", order=1,
            albums=[Album(slug="a", title="A", order=1, tracks=[Track(trackNumber=1, title="T", src="t.mp3")])]
        ).save()
        payload = [{**_VALID_ARTIST_PAYLOAD, "_id": str(other_artist.id)}]
        response = client.put("/api/artists", json=payload, headers=auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "Artist not found"}

    def test_returns_artist_data_in_response(self, client, auth_headers):
        response = client.put("/api/artists", json=[_VALID_ARTIST_PAYLOAD], headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert data[0]["title"] == "Artist 1"
        assert "user" not in data[0]


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

    def test_artist_cannot_delete_other_artist_document(self, client, auth_headers):
        other = User(email="other@test.com", password="x", role="artist", is_active=False).save()
        other_artist = Artist(
            user=other, slug="other", title="Other", order=1,
            albums=[Album(slug="a", title="A", order=1, tracks=[Track(trackNumber=1, title="T", src="t.mp3")])]
        ).save()
        response = client.delete(f"/api/artists/{other_artist.id}", headers=auth_headers)
        assert response.status_code == 404
        assert Artist.objects.count() == 1