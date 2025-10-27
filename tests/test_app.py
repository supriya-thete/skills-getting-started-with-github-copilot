from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200 or response.status_code == 307

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0

    # Verify activity structure
    for activity_name, details in activities.items():
        assert isinstance(activity_name, str)
        assert isinstance(details, dict)
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)

def test_signup_flow():
    # Get initial state
    response = client.get("/activities")
    activities = response.json()
    test_activity = list(activities.keys())[0]
    test_email = "test_student@mergington.edu"
    
    # Try to sign up
    response = client.post(f"/activities/{test_activity}/signup?email={test_email}")
    assert response.status_code == 200
    assert "message" in response.json()
    assert test_email in response.json()["message"]
    
    # Verify student was added
    response = client.get("/activities")
    activities = response.json()
    assert test_email in activities[test_activity]["participants"]
    
    # Try to sign up again (should fail)
    response = client.post(f"/activities/{test_activity}/signup?email={test_email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_unregister_flow():
    # First sign up a test student
    test_activity = "Chess Club"
    test_email = "test_unregister@mergington.edu"
    
    # Sign up the student
    client.post(f"/activities/{test_activity}/signup?email={test_email}")
    
    # Try to unregister
    response = client.delete(f"/activities/{test_activity}/unregister?email={test_email}")
    assert response.status_code == 200
    assert "message" in response.json()
    assert test_email in response.json()["message"]
    
    # Verify student was removed
    response = client.get("/activities")
    activities = response.json()
    assert test_email not in activities[test_activity]["participants"]
    
    # Try to unregister again (should fail)
    response = client.delete(f"/activities/{test_activity}/unregister?email={test_email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()

def test_nonexistent_activity():
    fake_activity = "Fake Activity Club"
    test_email = "test_student@mergington.edu"
    
    # Try to sign up for non-existent activity
    response = client.post(f"/activities/{fake_activity}/signup?email={test_email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    
    # Try to unregister from non-existent activity
    response = client.delete(f"/activities/{fake_activity}/unregister?email={test_email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()