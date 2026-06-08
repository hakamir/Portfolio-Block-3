import pytest
from io import BytesIO
from flask import Response
from unittest.mock import patch, MagicMock


def _audio_data(filename='test.mp3', mimetype='audio/mpeg'):
    return (BytesIO(b'fake audio data'), filename, mimetype)


def _image_data(filename='test.webp', mimetype='image/webp'):
    return (BytesIO(b'fake image data'), filename, mimetype)


class TestServeFile:
    def test_serves_file_without_authentication(self, client):
        with patch('routes.uploads.send_from_directory', return_value=Response('', 200)):
            response = client.get("/api/upload/artist-1/album-1/track.mp3")
        assert response.status_code == 200


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
    def _make_payload(self, destination):
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

    def test_uploads_to_hero(self, client, auth_headers):
        with patch('routes.uploads.is_valid_webp', return_value=True), \
                patch('werkzeug.datastructures.FileStorage.save'):
            response = client.post("/api/upload/background",
                                   data=self._make_payload('hero'),
                                   content_type='multipart/form-data',
                                   headers=auth_headers)
        assert response.status_code == 201
        assert response.get_json() == {'uploaded': True}

    def test_uploads_to_portfolio(self, client, auth_headers):
        with patch('routes.uploads.is_valid_webp', return_value=True), \
                patch('werkzeug.datastructures.FileStorage.save'):
            response = client.post("/api/upload/background",
                                   data=self._make_payload('portfolio'),
                                   content_type='multipart/form-data',
                                   headers=auth_headers)
        assert response.status_code == 201
        assert response.get_json() == {'uploaded': True}

    def test_uploads_to_biography(self, client, auth_headers):
        with patch('routes.uploads.is_valid_webp', return_value=True), \
                patch('werkzeug.datastructures.FileStorage.save'):
            response = client.post("/api/upload/background",
                                   data=self._make_payload('biography'),
                                   content_type='multipart/form-data',
                                   headers=auth_headers)
        assert response.status_code == 201
        assert response.get_json() == {'uploaded': True}
