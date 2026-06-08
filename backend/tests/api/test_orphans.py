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

    def test_returns_orphan_files(self, client, auth_headers, test_artist):
        with patch('routes.orphans.get_files', return_value=_ORPHAN_AUDIO_FILES):
            response = client.get("/api/orphans/audio", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == _ORPHAN_AUDIO_FILES


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
