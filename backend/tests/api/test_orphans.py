import pytest
from datetime import datetime, timezone
from unittest.mock import patch

from models.artist import Artist, Album, Track
from models.gallery import Gallery, GalleryImage
from models.orphan_audio import OrphanAudio
from models.orphan_gallery import OrphanGallery

# AUDIO
_ARTIST_SLUG = "artist-uuid-1"
_ALBUM_SLUG = "album-uuid-1"
_TRACK_SRC = "track-uuid-1.mp3"
_ORPHAN_SRC = "orphan-uuid.mp3"

# GALLERY
_GALLERY_SLUG = "gallery-uuid-1"
_IMAGE_SRC = "image-uuid-1.webp"


@pytest.fixture
def test_artist(test_artist_user):
    return Artist(
        user=test_artist_user,
        slug=_ARTIST_SLUG,
        title="Artist 1",
        order=1,
        albums=[Album(
            slug=_ALBUM_SLUG,
            title="Album 1",
            order=1,
            tracks=[Track(trackNumber=1, title="Track 1", src=_TRACK_SRC)]
        )]
    ).save()


@pytest.fixture
def test_gallery(test_artist_user):
    return Gallery(
        user=test_artist_user,
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


@pytest.fixture
def test_orphan_audio(test_artist_user):
    return OrphanAudio(
        user=test_artist_user,
        artist_id=None,
        artist_slug=_ARTIST_SLUG,
        artist_title="Artist 1",
        album_slug=_ALBUM_SLUG,
        album_title="Album 1",
        track_title="Orphan Track",
        track_number=2,
        track_src=_ORPHAN_SRC,
        tags=[],
        deleted_at=datetime.now(timezone.utc),
    ).save()


@pytest.fixture
def test_orphan_gallery(test_artist_user):
    return OrphanGallery(
        user=test_artist_user,
        gallery_slug=_GALLERY_SLUG,
        gallery_title="Gallery 1",
        image_src=_IMAGE_SRC,
        image_title="Image 1",
        image_location="Somewhere",
        image_date=datetime.now(timezone.utc),
        image_alt="Image 1, Paris, 2024",
        image_order=1,
        deleted_at=datetime.now(timezone.utc),
    ).save()


class TestGetOrphanAudio:
    def test_requires_authentication(self, client):
        response = client.get("/api/orphans/audio")
        assert response.status_code == 401

    def test_returns_empty_list_when_no_orphans(self, client, auth_headers):
        response = client.get("/api/orphans/audio", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == []

    def test_returns_orphan_records(self, client, auth_headers, test_orphan_audio):
        response = client.get("/api/orphans/audio", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['_id'] == str(test_orphan_audio.id)
        assert data[0]['artist_title'] == 'Artist 1'
        assert data[0]['album_title'] == 'Album 1'
        assert data[0]['track_title'] == 'Orphan Track'
        assert data[0]['src'] == f'{_ARTIST_SLUG}/{_ALBUM_SLUG}/{_ORPHAN_SRC}'


class TestRollbackOrphanAudio:
    def test_requires_authentication(self, client):
        response = client.post("/api/orphans/audio/rollback", json={"ids": []})
        assert response.status_code == 401

    def test_returns_400_on_missing_ids(self, client, auth_headers):
        response = client.post("/api/orphans/audio/rollback", json={}, headers=auth_headers)
        assert response.status_code == 400

    def test_returns_400_on_invalid_ids_type(self, client, auth_headers):
        response = client.post(
            "/api/orphans/audio/rollback",
            json={"ids": "not-a-list"},
            headers=auth_headers
        )
        assert response.status_code == 400

    def test_fails_if_file_not_found(self, client, auth_headers, test_orphan_audio):
        with patch('os.path.exists', return_value=False):
            response = client.post(
                "/api/orphans/audio/rollback",
                json={"ids": [str(test_orphan_audio.id)]},
                headers=auth_headers
            )
        assert response.status_code == 200
        data = response.get_json()
        assert data['restored'] == []
        assert data['failed'][0]['id'] == str(test_orphan_audio.id)
        assert data['failed'][0]['error'] == 'File not found'
        assert OrphanAudio.objects.count() == 1

    def test_restores_orphan_creating_new_artist(self, client, auth_headers, test_orphan_audio):
        with patch('os.path.exists', return_value=True):
            response = client.post(
                "/api/orphans/audio/rollback",
                json={"ids": [str(test_orphan_audio.id)]},
                headers=auth_headers
            )
        assert response.status_code == 200
        data = response.get_json()
        assert str(test_orphan_audio.id) in data['restored']
        assert data['failed'] == []
        assert OrphanAudio.objects.count() == 0
        artist = Artist.objects(slug=_ARTIST_SLUG).first()
        assert artist is not None
        assert artist.albums[0].tracks[0].src == _ORPHAN_SRC

    def test_restores_orphan_into_existing_artist(self, client, auth_headers, test_artist, test_orphan_audio):
        with patch('os.path.exists', return_value=True):
            response = client.post(
                "/api/orphans/audio/rollback",
                json={"ids": [str(test_orphan_audio.id)]},
                headers=auth_headers
            )
        assert response.status_code == 200
        data = response.get_json()
        assert str(test_orphan_audio.id) in data['restored']
        artist = Artist.objects(slug=_ARTIST_SLUG).first()
        srcs = [t.src for t in artist.albums[0].tracks]
        assert _ORPHAN_SRC in srcs

    def test_skips_already_existing_track(self, client, auth_headers, test_artist, test_artist_user):
        orphan = OrphanAudio(
            user=test_artist_user,
            artist_id=test_artist.id,
            artist_slug=_ARTIST_SLUG,
            artist_title="Artist 1",
            album_slug=_ALBUM_SLUG,
            album_title="Album 1",
            track_title="Track 1",
            track_number=1,
            track_src=_TRACK_SRC,
            tags=[],
            deleted_at=datetime.now(timezone.utc),
        ).save()
        with patch('os.path.exists', return_value=True):
            response = client.post(
                "/api/orphans/audio/rollback",
                json={"ids": [str(orphan.id)]},
                headers=auth_headers
            )
        assert response.status_code == 200
        data = response.get_json()
        assert str(orphan.id) in data['restored']
        artist = Artist.objects(slug=_ARTIST_SLUG).first()
        srcs = [t.src for t in artist.albums[0].tracks]
        assert srcs.count(_TRACK_SRC) == 1

    def test_partial_failure_returns_200(self, client, auth_headers, test_orphan_audio, test_artist_user):
        missing_orphan = OrphanAudio(
            user=test_artist_user,
            artist_id=None,
            artist_slug=_ARTIST_SLUG,
            artist_title="Artist 1",
            album_slug=_ALBUM_SLUG,
            album_title="Album 1",
            track_title="Missing File",
            track_number=3,
            track_src="no-file.mp3",
            tags=[],
            deleted_at=datetime.now(timezone.utc),
        ).save()

        def file_exists(path):
            return _ORPHAN_SRC in path

        with patch('os.path.exists', side_effect=file_exists):
            response = client.post(
                "/api/orphans/audio/rollback",
                json={"ids": [str(test_orphan_audio.id), str(missing_orphan.id)]},
                headers=auth_headers
            )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['restored']) == 1
        assert len(data['failed']) == 1
        assert data['failed'][0]['id'] == str(missing_orphan.id)


class TestDeleteOrphanAudio:
    def test_requires_authentication(self, client):
        response = client.delete("/api/orphans/audio", json={"ids": []})
        assert response.status_code == 401

    def test_returns_400_on_missing_ids(self, client, auth_headers):
        response = client.delete("/api/orphans/audio", json={}, headers=auth_headers)
        assert response.status_code == 400

    def test_returns_empty_deleted_on_empty_ids(self, client, auth_headers):
        response = client.delete("/api/orphans/audio", json={"ids": []}, headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == {"deleted": []}

    def test_deletes_orphan_doc_and_file(self, client, auth_headers, test_orphan_audio):
        with patch('os.path.exists', return_value=True), patch('os.remove') as mock_remove:
            response = client.delete(
                "/api/orphans/audio",
                json={"ids": [str(test_orphan_audio.id)]},
                headers=auth_headers
            )
        assert response.status_code == 200
        assert str(test_orphan_audio.id) in response.get_json()['deleted']
        assert mock_remove.call_count == 1
        assert OrphanAudio.objects.count() == 0

    def test_deletes_orphan_doc_even_if_file_missing(self, client, auth_headers, test_orphan_audio):
        with patch('os.path.exists', return_value=False), patch('os.remove') as mock_remove:
            response = client.delete(
                "/api/orphans/audio",
                json={"ids": [str(test_orphan_audio.id)]},
                headers=auth_headers
            )
        assert response.status_code == 200
        assert str(test_orphan_audio.id) in response.get_json()['deleted']
        mock_remove.assert_not_called()
        assert OrphanAudio.objects.count() == 0

    def test_skips_invalid_id_format(self, client, auth_headers):
        response = client.delete("/api/orphans/audio", json={"ids": ["not-valid"]}, headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()['deleted'] == []


class TestGetOrphanGallery:
    def test_requires_authentication(self, client):
        response = client.get("/api/orphans/gallery")
        assert response.status_code == 401

    def test_returns_empty_list_when_no_orphans(self, client, auth_headers):
        response = client.get("/api/orphans/gallery", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == []

    def test_returns_orphan_records(self, client, auth_headers, test_orphan_gallery):
        response = client.get("/api/orphans/gallery", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['_id'] == str(test_orphan_gallery.id)
        assert data[0]['gallery_title'] == 'Gallery 1'
        assert data[0]['image_title'] == 'Image 1'
        assert data[0]['src'] == f'{_GALLERY_SLUG}/{_IMAGE_SRC}'


class TestDeleteOrphanGallery:
    def test_requires_authentication(self, client):
        response = client.delete("/api/orphans/gallery", json={"files": []})
        assert response.status_code == 401

    def test_returns_400_on_missing_ids(self, client, auth_headers):
        response = client.delete("/api/orphans/gallery", json={}, headers=auth_headers)
        assert response.status_code == 400

    def test_returns_empty_deleted_on_empty_ids(self, client, auth_headers):
        response = client.delete("/api/orphans/gallery", json={"ids": []}, headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == {"deleted": []}

    def test_deletes_orphan_doc_and_file(self, client, auth_headers, test_orphan_gallery):
        with patch('os.path.exists', return_value=True), patch('os.remove') as mock_remove:
            response = client.delete(
                "/api/orphans/gallery",
                json={"ids": [str(test_orphan_gallery.id)]},
                headers=auth_headers
            )
        assert response.status_code == 200
        assert str(test_orphan_gallery.id) in response.get_json()['deleted']
        assert mock_remove.call_count == 1
        assert OrphanGallery.objects.count() == 0

    def test_deletes_orphan_doc_even_if_file_missing(self, client, auth_headers, test_orphan_gallery):
        with patch('os.path.exists', return_value=False), patch('os.remove') as mock_remove:
            response = client.delete(
                "/api/orphans/gallery",
                json={"ids": [str(test_orphan_gallery.id)]},
                headers=auth_headers
            )
        assert response.status_code == 200
        assert str(test_orphan_gallery.id) in response.get_json()['deleted']
        mock_remove.assert_not_called()
        assert OrphanGallery.objects.count() == 0

    def test_skips_invalid_id_format(self, client, auth_headers):
        response = client.delete("/api/orphans/gallery", json={"ids": ["not-valid"]}, headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()['deleted'] == []
