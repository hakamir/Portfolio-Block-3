import pytest

from models.message import Message
from models.user import User
from tests.conftest import test_artist_user

_VALID_PAYLOAD = {"name": "Test User", "email": "test@example.com", "message": "Hello"}
_NONEXISTENT_ID = "000000000000000000000001"


@pytest.fixture
def test_message(test_artist_user):
    return Message(
        user=test_artist_user,
        name="Test User",
        email="test@example.com",
        message="Hello",
        read=False,
        trashed=False,
        replied=False
    ).save()


class TestGetMessages:
    def test_requires_authentication(self, client):
        response = client.get("/api/messages")
        assert response.status_code == 401

    def test_returns_empty_list_when_no_messages(self, client, auth_headers):
        response = client.get("/api/messages", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == []

    def test_returns_messages(self, client, auth_headers, test_message):
        response = client.get("/api/messages", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "Test User"
        assert "_id" in data[0]

    def test_artist_only_sees_own_messages(self, client, auth_headers, test_artist_user):
        Message(user=test_artist_user, name="Test", email="test@example.com", message="Message").save()
        other = User(email="other@test.com", password="x", role="artist").save()
        Message(user=other, name="Other", email="other@example.com", message="Other").save()

        response = client.get("/api/messages", headers=auth_headers)
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "Test"


class TestCreateMessage:
    def test_returns_400_on_invalid_payload(self, client):
        response = client.post("/api/messages", json={"name": "No email"})
        assert response.status_code == 400
        assert response.get_json() == {"error": "Invalid payload"}

    def test_returns_404_when_no_active_artist(self, client):
        response = client.post("/api/messages", json=_VALID_PAYLOAD)
        assert response.status_code == 404
        assert response.get_json() == {"error": "No active artist found"}

    def test_creates_message(self, client, test_artist_user):
        response = client.post("/api/messages", json=_VALID_PAYLOAD)
        assert response.status_code == 201
        assert response.get_json() == {"created": True}
        assert Message.objects(user=test_artist_user).count() == 1


class TestUpdateMessage:
    def test_requires_authentication(self, client, test_message):
        response = client.patch(f"/api/messages/{test_message.id}", json={"read": True})
        assert response.status_code == 401

    def test_returns_400_on_invalid_payload(self, client, auth_headers, test_message):
        response = client.patch(f"/api/messages/{test_message.id}",
                                json={"unknown_field": True}, headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Invalid payload"}

    def test_returns_404_when_message_not_found(self, client, auth_headers):
        response = client.patch(f"/api/messages/{_NONEXISTENT_ID}",
                                json={"read": True}, headers=auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "Message not found"}

    def test_marks_message_as_read(self, client, auth_headers, test_message):
        response = client.patch(f"/api/messages/{test_message.id}",
                                json={"read": True}, headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == {"updated": True}
        assert Message.objects.get(id=test_message.id).read is True

    def test_marks_message_as_replied_and_sets_replied_at(self, client, auth_headers, test_message):
        response = client.patch(f"/api/messages/{test_message.id}",
                                json={"replied": True}, headers=auth_headers)
        assert response.status_code == 200
        updated = Message.objects.get(id=test_message.id)
        assert updated.replied is True
        assert updated.replied_at is not None

    def test_returns_400_on_empty_payload(self, client, auth_headers, test_message):
        response = client.patch(f"/api/messages/{test_message.id}",
                                json={}, headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "No fields to update"}

    def test_artist_cannot_update_other_artist_message(self, client, auth_headers):
        other = User(email="other@test.com", password="x", role="artist", is_active=False).save()
        msg = Message(user=other, name="Other", email="b@b.com", message="World").save()

        response = client.patch(f"/api/messages/{msg.id}",
                                json={"read": True}, headers=auth_headers)
        assert response.status_code == 404


class TestDeleteMessage:
    def test_requires_authentication(self, client, test_message):
        response = client.delete(f"/api/messages/{test_message.id}")
        assert response.status_code == 401

    def test_returns_400_on_invalid_id_format(self, client, auth_headers):
        response = client.delete("/api/messages/not-valid", headers=auth_headers)
        assert response.status_code == 400
        assert response.get_json() == {"error": "Invalid ID"}

    def test_returns_404_when_message_not_found(self, client, auth_headers):
        response = client.delete(f"/api/messages/{_NONEXISTENT_ID}", headers=auth_headers)
        assert response.status_code == 404
        assert response.get_json() == {"error": "Message not Found"}

    def test_deletes_message(self, client, auth_headers, test_message):
        response = client.delete(f"/api/messages/{test_message.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == {"deleted": True}
        assert Message.objects.count() == 0

    def test_artist_cannot_delete_other_artist_message(self, client, auth_headers):
        other = User(email="other@test.com", password="x", role="artist", is_active=False).save()
        msg = Message(user=other, name="Other", email="b@b.com", message="World").save()

        response = client.delete(f"/api/messages/{msg.id}", headers=auth_headers)
        assert response.status_code == 404
        assert Message.objects.count() == 1
