import uuid

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_get_activities_returns_catalog():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]
    assert isinstance(payload["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_email_to_participants():
    activity_name = "Programming Class"
    email = f"student-{uuid.uuid4().hex[:8]}@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in client.get("/activities").json()[activity_name]["participants"]

    cleanup = client.delete(f"/activities/{activity_name}/signup?email={email}")
    assert cleanup.status_code == 200


def test_signup_rejects_duplicate_email():
    activity_name = "Chess Club"
    email = f"duplicate-{uuid.uuid4().hex[:8]}@mergington.edu"

    first_signup = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert first_signup.status_code == 200

    second_signup = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert second_signup.status_code == 400
    assert second_signup.json()["detail"] == "Student is already signed up for this activity"

    cleanup = client.delete(f"/activities/{activity_name}/signup?email={email}")
    assert cleanup.status_code == 200


def test_unregister_removes_email_from_activity():
    activity_name = "Programming Class"
    email = f"student-{uuid.uuid4().hex[:8]}@mergington.edu"

    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200

    delete_response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    assert delete_response.status_code == 200
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_raises_for_missing_email():
    activity_name = "Chess Club"
    email = f"missing-{uuid.uuid4().hex[:8]}@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_signup_raises_for_unknown_activity():
    email = f"unknown-{uuid.uuid4().hex[:8]}@mergington.edu"

    response = client.post("/activities/Unknown Activity/signup?email={email}".format(email=email))

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
