import pytest
from io import BytesIO
from flask import Response
from unittest.mock import patch, MagicMock

from models.background import Background, BackgroundImage
from models.user import User


def _audio_data(filename='test.mp3', mimetype='audio/mpeg'):
    return (BytesIO(b'fake audio data'), filename, mimetype)


def _image_data(filename='test.webp', mimetype='image/webp'):
    return (BytesIO(b'fake image data'), filename, mimetype)


class TestServeFile:
    def test_serves_file_without_authentication(self, client):
        with patch('routes.uploads.send_from_directory', return_value=Response('', 200)):
            response = client.get("/api/upload/artist-1/album-1/track.mp3")
        assert response.status_code == 200

    def test_serves_file_as_attachment(self, client):
        with patch('routes.uploads.send_from_directory', return_value=Response('', 200)) as mock:
            client.get("/api/upload/test/file.mp3?download=true")
        _, kwargs = mock.call_args
        assert kwargs['as_attachment'] is True

class TestUploadAudio:
    def test_requires_authentication(self, client):
        response = client.post("/api/upload/audio", data={
            'file': _audio_data(),
            'artistSlug': 'artist-1',
            'albumSlug': 'album-1',
            'trackSrc': 'track.mp3'
        }, content_type='multipart/form-data')
        assert response.status_code == 401

    def test_returns_400_when_no_file(self, client, auth_headers):
        response = client.post("/api/upload/audio", data={},
                               content_type='multipart/form-data',
                               headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {'error': 'No file part'}

    def test_returns_415_on_invalid_mime_type(self, client, auth_headers):
        response = client.post("/api/upload/audio", data={
            'file': (BytesIO(b'data'), 'test.txt', 'text/plain'),
        }, content_type='multipart/form-data', headers=auth_headers)
        assert response.status_code == 415
        assert response.get_json() == {'error': 'Invalid mime type'}

    def test_returns_415_on_invalid_extension(self, client, auth_headers):
        response = client.post("/api/upload/audio", data={
            'file': (BytesIO(b'data'), 'test.exe', 'audio/mpeg'),
        }, content_type='multipart/form-data', headers=auth_headers)
        assert response.status_code == 415
        assert response.get_json() == {'error': 'Invalid file type'}

    def test_returns_400_when_missing_form_fields(self, client, auth_headers):
        response = client.post("/api/upload/audio", data={
            'file': _audio_data(),
        }, content_type='multipart/form-data', headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {'error': 'Missing required fields'}

    def test_returns_500_on_conversion_failure(self, client, auth_headers):
        with patch('routes.uploads.AudioConverter.to_mp3', side_effect=ValueError):
            response = client.post("/api/upload/audio", data={
                'file': _audio_data('test.ogg', 'audio/ogg'),
                'artistSlug': 'artist-1',
                'albumSlug': 'album-1',
                'trackSrc': 'track.ogg'
            }, content_type='multipart/form-data', headers=auth_headers)
        assert response.status_code == 500
        assert response.get_json() == {'error': 'File conversion failed'}

    def test_uploads_audio_file(self, client, auth_headers):
        mock_converted = MagicMock()
        with patch('routes.uploads.AudioConverter.to_mp3', return_value=mock_converted), \
                patch('routes.uploads.os.makedirs'):
            response = client.post("/api/upload/audio", data={
                'file': _audio_data(),
                'artistSlug': 'artist-1',
                'albumSlug': 'album-1',
                'trackSrc': 'track.mp3'
            }, content_type='multipart/form-data', headers=auth_headers)
        assert response.status_code == 201
        assert response.get_json() == {'uploaded': True}
        assert mock_converted.save.called


class TestUploadGallery:
    def test_requires_authentication(self, client):
        response = client.post("/api/upload/gallery", data={
            'file': _image_data(),
            'gallerySlug': 'gallery-1',
            'imageSrc': 'image.webp'
        }, content_type='multipart/form-data')
        assert response.status_code == 401

    def test_returns_400_when_no_file(self, client, auth_headers):
        response = client.post("/api/upload/gallery", data={},
                               content_type='multipart/form-data',
                               headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {'error': 'No file part'}

    def test_returns_415_on_invalid_mime_type(self, client, auth_headers):
        response = client.post("/api/upload/gallery", data={
            'file': (BytesIO(b'data'), 'test.txt', 'text/plain'),
        }, content_type='multipart/form-data', headers=auth_headers)
        assert response.status_code == 415
        assert response.get_json() == {'error': 'Invalid mime type'}

    def test_returns_415_on_invalid_extension(self, client, auth_headers):
        response = client.post("/api/upload/gallery", data={
            'file': (BytesIO(b'data'), 'test.exe', 'image/jpeg'),
        }, content_type='multipart/form-data', headers=auth_headers)
        assert response.status_code == 415
        assert response.get_json() == {'error': 'Invalid file type'}

    def test_returns_400_when_missing_form_fields(self, client, auth_headers):
        response = client.post("/api/upload/gallery", data={
            'file': _image_data(),
        }, content_type='multipart/form-data', headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {'error': 'Missing required fields'}

    def test_uploads_image_file(self, client, auth_headers):
        with patch('routes.uploads.os.makedirs'), \
                patch('werkzeug.datastructures.FileStorage.save'):
            response = client.post("/api/upload/gallery", data={
                'file': _image_data(),
                'gallerySlug': 'gallery-1',
                'imageSrc': 'image.webp'
            }, content_type='multipart/form-data', headers=auth_headers)
        assert response.status_code == 201
        assert response.get_json() == {'uploaded': True}


class TestUploadBackground:
    @staticmethod
    def _make_payload(destination):
        return {
            'destination': destination,
            'image-2048': _image_data('img-2048.webp'),
            'image-1024': _image_data('img-1024.webp'),
            'image-512': _image_data('img-512.webp'),
        }

    def test_requires_authentication(self, client):
        response = client.post("/api/upload/background",
                               data=self._make_payload('hero'),
                               content_type='multipart/form-data')
        assert response.status_code == 401

    def test_returns_400_when_missing_required_fields(self, client, auth_headers):
        response = client.post("/api/upload/background",
                               data={},
                               content_type='multipart/form-data',
                               headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {'error': 'Missing required fields'}

    def test_returns_400_on_invalid_file(self, client, auth_headers):
        with patch('routes.uploads.is_valid_webp', return_value=False):
            response = client.post("/api/upload/background",
                                   data=self._make_payload('hero'),
                                   content_type='multipart/form-data',
                                   headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {'error': 'Invalid file'}

    def test_returns_400_on_invalid_destination(self, client, auth_headers):
        with patch('routes.uploads.is_valid_webp', return_value=True):
            response = client.post("/api/upload/background",
                                   data=self._make_payload('unknown'),
                                   content_type='multipart/form-data',
                                   headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {'error': 'Invalid destination'}

    def test_uploads_to_hero_and_updates_background(self, client, auth_headers, test_artist_user):
        with patch('routes.uploads.is_valid_webp', return_value=True), \
                patch('os.makedirs'), \
                patch('werkzeug.datastructures.FileStorage.save'):
            response = client.post("/api/upload/background",
                                   data=self._make_payload('hero'),
                                   content_type='multipart/form-data',
                                   headers=auth_headers)
        assert response.status_code == 201
        assert response.get_json() == {'uploaded': True}
        # Check creation in database
        bg = Background.objects(user=test_artist_user).first()
        assert bg is not None
        assert bg.hero is not None
        assert test_artist_user.storage_id in bg.hero.sm

    def test_uploads_to_portfolio(self, client, auth_headers, test_artist_user):
        with patch('routes.uploads.is_valid_webp', return_value=True), \
                patch('os.makedirs'), \
                patch('werkzeug.datastructures.FileStorage.save'):
            response = client.post("/api/upload/background",
                                   data=self._make_payload('portfolio'),
                                   content_type='multipart/form-data',
                                   headers=auth_headers)
        assert response.status_code == 201
        bg = Background.objects(user=test_artist_user).first()
        assert bg.portfolio is not None

    def test_uploads_to_biography(self, client, auth_headers, test_artist_user):
        with patch('routes.uploads.is_valid_webp', return_value=True), \
                patch('os.makedirs'), \
                patch('werkzeug.datastructures.FileStorage.save'):
            response = client.post("/api/upload/background",
                                   data=self._make_payload('biography'),
                                   content_type='multipart/form-data',
                                   headers=auth_headers)
        assert response.status_code == 201
        bg = Background.objects(user=test_artist_user).first()
        assert bg.biography is not None

    def test_updates_existing_background(self, client, auth_headers, test_artist_user):
        # Background document exists: must be updated, no duplicate
        Background(
            user=test_artist_user,
            hero=BackgroundImage(sm='/old-512.webp', md='/old-1024.webp', lg='/old-2048.webp'),
            portfolio=BackgroundImage(sm='/p-512.webp', md='/p-1024.webp', lg='/p-2048.webp'),
            biography=BackgroundImage(sm='/b-512.webp', md='/b-1024.webp', lg='/b-2048.webp')
        ).save()

        with patch('routes.uploads.is_valid_webp', return_value=True), \
                patch('os.makedirs'), \
                patch('werkzeug.datastructures.FileStorage.save'):
            response = client.post("/api/upload/background",
                                   data=self._make_payload('hero'),
                                   content_type='multipart/form-data',
                                   headers=auth_headers)
        assert response.status_code == 201
        # One document in database only
        assert Background.objects(user=test_artist_user).count() == 1
        # URL updated
        bg = Background.objects(user=test_artist_user).first()
        assert '/old-512.webp' not in bg.hero.sm


class TestGetActiveBackgrounds:
    def test_returns_404_when_no_active_artist(self, client):
        response = client.get("/api/upload/background")
        assert response.status_code == 404
        assert response.get_json() == {'error': 'No active artist found'}

    def test_returns_404_when_no_background(self, client, test_artist_user):
        # Active artist but no document in database
        response = client.get("/api/upload/background")
        assert response.status_code == 404
        assert response.get_json() == {'error': 'No background found'}

    def test_returns_active_backgrounds(self, client, test_artist_user):
        Background(
            user=test_artist_user,
            hero=BackgroundImage(
                sm='/upload/background/placeholder/hero/hero-512.webp',
                md='/upload/background/placeholder/hero/hero-1024.webp',
                lg='/upload/background/placeholder/hero/hero-2048.webp'
            ),
            portfolio=BackgroundImage(
                sm='/upload/background/placeholder/portfolio/portfolio-512.webp',
                md='/upload/background/placeholder/portfolio/portfolio-1024.webp',
                lg='/upload/background/placeholder/portfolio/portfolio-2048.webp'
            ),
            biography=BackgroundImage(
                sm='/upload/background/placeholder/biography/biography-512.webp',
                md='/upload/background/placeholder/biography/biography-1024.webp',
                lg='/upload/background/placeholder/biography/biography-2048.webp'
            )
        ).save()

        response = client.get("/api/upload/background")
        assert response.status_code == 200
        data = response.get_json()
        assert 'hero' in data
        assert 'portfolio' in data
        assert 'biography' in data
        assert 'user' not in data
        assert data['hero']['sm'] == '/upload/background/placeholder/hero/hero-512.webp'


class TestGetOwnedBackgrounds:
    def test_requires_authentication(self, client):
        response = client.get("/api/upload/background/dashboard")
        assert response.status_code == 401

    def test_returns_404_when_no_background(self, client, auth_headers):
        response = client.get("/api/upload/background/dashboard", headers=auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {'error': 'No background found'}

    def test_returns_owned_backgrounds(self, client, auth_headers, test_artist_user):
        Background(
            user=test_artist_user,
            hero=BackgroundImage(
                sm='/upload/background/placeholder/hero/hero-512.webp',
                md='/upload/background/placeholder/hero/hero-1024.webp',
                lg='/upload/background/placeholder/hero/hero-2048.webp'
            ),
            portfolio=BackgroundImage(
                sm='/upload/background/placeholder/portfolio/portfolio-512.webp',
                md='/upload/background/placeholder/portfolio/portfolio-1024.webp',
                lg='/upload/background/placeholder/portfolio/portfolio-2048.webp'
            ),
            biography=BackgroundImage(
                sm='/upload/background/placeholder/biography/biography-512.webp',
                md='/upload/background/placeholder/biography/biography-1024.webp',
                lg='/upload/background/placeholder/biography/biography-2048.webp'
            )
        ).save()

        response = client.get("/api/upload/background/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'hero' in data
        assert 'portfolio' in data
        assert 'biography' in data
        assert 'user' not in data

    def test_artist_only_sees_own_backgrounds(self, client, auth_headers, test_artist_user):
        # Create a second artist with their own Background
        other = User(
            email="other@test.com",
            password="x",
            role="artist",
            is_active=False
        ).save()
        Background(
            user=other,
            hero=BackgroundImage(sm='/other/hero-512.webp', md='/other/hero-1024.webp', lg='/other/hero-2048.webp'),
            portfolio=BackgroundImage(sm='/other/p-512.webp', md='/other/p-1024.webp', lg='/other/p-2048.webp'),
            biography=BackgroundImage(sm='/other/b-512.webp', md='/other/b-1024.webp', lg='/other/b-2048.webp')
        ).save()

        # No background for test_artist_user -> 404
        response = client.get("/api/upload/background/dashboard", headers=auth_headers)
        assert response.status_code == 404
