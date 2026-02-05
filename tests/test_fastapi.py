from fastapi.testclient import TestClient
from src.app import app, activities


client = TestClient(app)


def test_root_redirects_to_static_index():
    r = client.get("/")
    assert r.status_code == 200
    assert "<html" in r.text.lower()


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    # ensure a known activity exists
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    # make sure email not already in participants
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # signup
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert email in activities[activity]["participants"]

    # signing up again should error
    r2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r2.status_code == 400

    # unregister
    r3 = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert r3.status_code == 200
    assert email not in activities[activity]["participants"]


def test_signup_nonexistent_activity():
    r = client.post("/activities/NoSuchActivity/signup", params={"email": "x@y.com"})
    assert r.status_code == 404


def test_unregister_not_signed_up():
    r = client.delete("/activities/Chess Club/participants", params={"email": "not@here.com"})
    assert r.status_code == 404
