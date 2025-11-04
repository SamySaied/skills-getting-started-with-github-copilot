import uuid

from fastapi.testclient import TestClient

import src.app as appmod


client = TestClient(appmod.app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # basic sanity: return is a dict with known activity
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_cycle():
    activity = "Chess Club"
    email = f"test+{uuid.uuid4().hex}@example.com"

    # Ensure not present initially
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]

    # Sign up (use params so special chars are encoded)
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]

    # Confirm present
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email in resp.json()[activity]["participants"]

    # Attempt duplicate signup -> should fail
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400

    # Unregister
    resp = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Unregistered" in resp.json()["message"]

    # Confirm removed
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]


def test_unregister_nonexistent_participant():
    activity = "Programming Class"
    email = f"nonexistent+{uuid.uuid4().hex}@example.com"

    # Ensure not present
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]

    # Try to unregister -> 404
    resp = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 404
