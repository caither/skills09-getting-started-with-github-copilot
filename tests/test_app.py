from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a deep copy of initial participants so tests can modify safely
    original = {
        name: {**data, "participants": list(data["participants"])}
        for name, data in activities.items()
    }
    yield
    # restore
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_duplicate_signup():
    email = "tester@mergington.edu"
    activity = "Chess Club"

    # signup success
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # duplicate signup should return 400
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400


def test_signup_activity_not_found():
    resp = client.post("/activities/Unknown/signup?email=a@b")
    assert resp.status_code == 404


def test_unregister_success_and_not_found():
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Ensure email is present initially
    assert email in activities[activity]["participants"]

    # unregister success
    resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]

    # unregister again should return 404 (participant not found)
    resp2 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp2.status_code == 404


def test_unregister_activity_not_found():
    resp = client.post("/activities/Unknown/unregister?email=a@b")
    assert resp.status_code == 404


def test_root_redirect():
    # ensure root redirects to the static index page
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (301, 302, 307, 308)
    assert resp.headers.get("location") == "/static/index.html"


def test_signup_and_unregister_response_messages():
    email = "message_test@mergington.edu"
    activity = "Programming Class"

    # signup should return a message key with expected content
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data
    assert email in data["message"]

    # unregister should return a message key as well
    resp2 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert "message" in data2
    assert email in data2["message"]
