import pytest
from datetime import datetime, timezone
from unittest.mock import patch

from models.artist import Artist, Album, Track
from models.gallery import Gallery, GalleryImage

_ORPHAN_AUDIO_FILES = ["artist-1/album-1/orphan.mp3"]
_ORPHAN_GALLERY_FILES = ["gallery-1/orphan.webp"]


@pytest.fixture
def test_artist():
    return Artist(
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


@pytest.fixture
def test_gallery():
    return Gallery(
        slug="gallery-1",
        title="Gallery 1",
        order=1,
        images=[GalleryImage(
            src="gallery-1_a296a2f6-5ff9-4e49-bd5a-23d16b34b863.webp",
            title="Image 1",
            location="Paris",
            date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            order=1,
            alt="Image 1, Paris, 2024"
        )]
    ).save()


class TestGetOrphanAudio:
    def test_requires_authentication(self, client):
        response = client.get("/api/orphans/audio")
        assert response.status_code == 401

    def test_returns_empty_list_when_no_orphans(self, client, auth_headers):
        with patch('routes.orphans.get_files', return_value=[]):
            response = client.get("/api/orphans/audio", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == []

    def test_returns_orphan_files_without_metadata(self, client, auth_headers, test_artist):
        with patch('routes.orphans.get_files', return_value=_ORPHAN_AUDIO_FILES), \
                patch('routes.orphans.read_id3_metadata', return_value=None):
            response = client.get("/api/orphans/audio", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == [
            {'file': 'artist-1/album-1/orphan.mp3', 'metadata': None}
        ]

    def test_returns_orphan_files_with_metadata(self, client, auth_headers, test_artist):
        metadata = {
            'artist': 'Artist 1',
            'album': 'Album 1',
            'title': 'Orphan Track',
            'track_number': 1
        }
        with patch('routes.orphans.get_files', return_value=_ORPHAN_AUDIO_FILES), \
                patch('routes.orphans.read_id3_metadata', return_value=metadata):
            response = client.get("/api/orphans/audio", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == [
            {'file': 'artist-1/album-1/orphan.mp3', 'metadata': metadata}
        ]


_ROLLBACK_METADATA = {
    'artist': 'Artist 1',
    'album': 'Album 1',
    'title': 'Orphan Track',
    'track_number': 1
}


class TestRollbackOrphanAudio:
    def test_requires_authentication(self, client):
        response = client.post("/api/orphans/audio/rollback", json={"files": []})
        assert response.status_code == 401

    def test_returns_400_on_missing_body(self, client, auth_headers):
        response = client.post("/api/orphans/audio/rollback",
                               json={}, headers=auth_headers)
        assert response.status_code == 400

    def test_returns_400_on_invalid_files_type(self, client, auth_headers):
        response = client.post("/api/orphans/audio/rollback",
                               json={"files": "not-a-list"}, headers=auth_headers)
        assert response.status_code == 400

    def test_fails_if_file_not_found(self, client, auth_headers):
        with patch('os.path.exists', return_value=False):
            response = client.post(
                "/api/orphans/audio/rollback",
                json={"files": _ORPHAN_AUDIO_FILES},
                headers=auth_headers
            )
        assert response.status_code == 200
        data = response.get_json()
        assert data['restored'] == []
        assert data['failed'][0]['file'] == _ORPHAN_AUDIO_FILES[0]
        assert data['failed'][0]['error'] == 'File not found'

    def test_fails_if_no_metadata(self, client, auth_headers):
        with patch('os.path.exists', return_value=True), \
                patch('routes.orphans.read_id3_metadata', return_value=None):
            response = client.post(
                "/api/orphans/audio/rollback",
                json={"files": _ORPHAN_AUDIO_FILES},
                headers=auth_headers
            )
        assert response.status_code == 200
        data = response.get_json()
        assert data['restored'] == []
        assert data['failed'][0]['error'] == 'No ID3 metadata found'

    def test_fails_on_invalid_path_structure(self, client, auth_headers):
        invalid_path = ["orphan.mp3"]  # un seul segment, pas 3
        with patch('os.path.exists', return_value=True), \
                patch('routes.orphans.read_id3_metadata', return_value=_ROLLBACK_METADATA):
            response = client.post(
                "/api/orphans/audio/rollback",
                json={"files": invalid_path},
                headers=auth_headers
            )
        assert response.status_code == 200
        data = response.get_json()
        assert data['restored'] == []
        assert data['failed'][0]['error'] == 'Unexpected path structure'

    def test_restores_orphan_creating_new_artist(self, client, auth_headers):
        # Aucun artiste en base — doit créer artiste + album + track
        with patch('os.path.exists', return_value=True), \
                patch('routes.orphans.read_id3_metadata', return_value=_ROLLBACK_METADATA):
            response = client.post(
                "/api/orphans/audio/rollback",
                json={"files": _ORPHAN_AUDIO_FILES},
                headers=auth_headers
            )
        assert response.status_code == 200
        data = response.get_json()
        assert _ORPHAN_AUDIO_FILES[0] in data['restored']
        assert data['failed'] == []

        # Vérifie que l'artiste a bien été créé en base
        artist = Artist.objects(slug="artist-1").first()
        assert artist is not None
        assert artist.albums[0].slug == "album-1"
        assert artist.albums[0].tracks[0].src == "orphan.mp3"

    def test_restores_orphan_into_existing_artist(self, client, auth_headers, test_artist):
        # L'artiste existe déjà, l'album aussi — doit ajouter le track
        orphan = ["artist-1/album-1/orphan.mp3"]
        with patch('os.path.exists', return_value=True), \
                patch('routes.orphans.read_id3_metadata', return_value=_ROLLBACK_METADATA):
            response = client.post(
                "/api/orphans/audio/rollback",
                json={"files": orphan},
                headers=auth_headers
            )
        assert response.status_code == 200
        data = response.get_json()
        assert orphan[0] in data['restored']

        artist = Artist.objects(slug="artist-1").first()
        srcs = [t.src for t in artist.albums[0].tracks]
        assert "orphan.mp3" in srcs

    def test_skips_already_existing_track(self, client, auth_headers, test_artist):
        # Le track existe déjà — doit être ignoré sans erreur
        existing = ["artist-1/album-1/track.mp3"]
        metadata = {**_ROLLBACK_METADATA, 'title': 'Track 1'}
        with patch('os.path.exists', return_value=True), \
                patch('routes.orphans.read_id3_metadata', return_value=metadata):
            response = client.post(
                "/api/orphans/audio/rollback",
                json={"files": existing},
                headers=auth_headers
            )
        assert response.status_code == 200
        data = response.get_json()
        # Restauré sans erreur, mais pas de doublon en base
        assert existing[0] in data['restored']
        artist = Artist.objects(slug="artist-1").first()
        srcs = [t.src for t in artist.albums[0].tracks]
        assert srcs.count("track.mp3") == 1

    def test_partial_failure_returns_200(self, client, auth_headers):
        # Un fichier valide, un sans metadata — résultat partiel
        files = [
            "artist-1/album-1/orphan.mp3",
            "artist-1/album-1/no_tags.mp3"
        ]

        def mock_metadata(path):
            if "orphan" in path:
                return _ROLLBACK_METADATA
            return None

        with patch('os.path.exists', return_value=True), \
                patch('routes.orphans.read_id3_metadata', side_effect=mock_metadata):
            response = client.post(
                "/api/orphans/audio/rollback",
                json={"files": files},
                headers=auth_headers
            )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['restored']) == 1
        assert len(data['failed']) == 1
        assert data['failed'][0]['file'] == "artist-1/album-1/no_tags.mp3"


class TestDeleteOrphanAudio:
    def test_requires_authentication(self, client):
        response = client.delete("/api/orphans/audio", json={"files": []})
        assert response.status_code == 401

    def test_returns_deleted_true_on_empty_list(self, client, auth_headers):
        with patch('routes.orphans.cleanup_empty_dirs'):
            response = client.delete("/api/orphans/audio", json={"files": []},
                                     headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == {"deleted": True}

    def test_deletes_existing_files(self, client, auth_headers):
        files = ["artist-1/album-1/track.mp3"]
        with patch('os.path.exists', return_value=True), \
                patch('os.remove') as mock_remove, \
                patch('routes.orphans.cleanup_empty_dirs'):
            response = client.delete("/api/orphans/audio", json={"files": files},
                                     headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == {"deleted": True}
        assert mock_remove.call_count == 1

    def test_skips_nonexistent_files(self, client, auth_headers):
        files = ["artist-1/album-1/missing.mp3"]
        with patch('os.path.exists', return_value=False), \
                patch('os.remove') as mock_remove, \
                patch('routes.orphans.cleanup_empty_dirs'):
            response = client.delete("/api/orphans/audio", json={"files": files},
                                     headers=auth_headers)
        assert response.status_code == 200
        assert mock_remove.call_count == 0


class TestGetOrphanGallery:
    def test_requires_authentication(self, client):
        response = client.get("/api/orphans/gallery")
        assert response.status_code == 401

    def test_returns_empty_list_when_no_orphans(self, client, auth_headers):
        with patch('routes.orphans.get_files', return_value=[]):
            response = client.get("/api/orphans/gallery", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == []

    def test_returns_orphan_files(self, client, auth_headers, test_gallery):
        with patch('routes.orphans.get_files', return_value=_ORPHAN_GALLERY_FILES):
            response = client.get("/api/orphans/gallery", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == _ORPHAN_GALLERY_FILES


class TestDeleteOrphanGallery:
    def test_requires_authentication(self, client):
        response = client.delete("/api/orphans/gallery", json={"files": []})
        assert response.status_code == 401

    def test_returns_deleted_true_on_empty_list(self, client, auth_headers):
        with patch('routes.orphans.cleanup_empty_dirs'):
            response = client.delete("/api/orphans/gallery", json={"files": []},
                                     headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == {"deleted": True}

    def test_deletes_existing_files(self, client, auth_headers):
        files = ["gallery-1/image.webp"]
        with patch('os.path.exists', return_value=True), \
                patch('os.remove') as mock_remove, \
                patch('routes.orphans.cleanup_empty_dirs'):
            response = client.delete("/api/orphans/gallery", json={"files": files},
                                     headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == {"deleted": True}
        assert mock_remove.call_count == 1

    def test_skips_nonexistent_files(self, client, auth_headers):
        files = ["gallery-1/missing.webp"]
        with patch('os.path.exists', return_value=False), \
                patch('os.remove') as mock_remove, \
                patch('routes.orphans.cleanup_empty_dirs'):
            response = client.delete("/api/orphans/gallery", json={"files": files},
                                     headers=auth_headers)
        assert response.status_code == 200
        assert mock_remove.call_count == 0
