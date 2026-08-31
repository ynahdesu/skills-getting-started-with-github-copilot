import uuid

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Programming Class"
    email = f"student-{uuid.uuid4().hex[:8]}@mergington.edu"

    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200

    delete_response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    assert delete_response.status_code == 200
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_participant_raises_for_missing_email():
    activity_name = "Chess Club"
    email = f"missing-{uuid.uuid4().hex[:8]}@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
