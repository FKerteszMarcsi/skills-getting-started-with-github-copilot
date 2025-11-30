"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice basketball skills and compete in inter-school tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "sarah@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Develop soccer techniques and participate in friendly matches",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore various art mediums including painting, drawing, and sculpture",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["isabella@mergington.edu", "ethan@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in plays and develop acting and theatrical production skills",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["charlotte@mergington.edu", "liam@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science competitions and conduct hands-on experiments",
            "schedule": "Tuesdays, 3:30 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["amelia@mergington.edu", "benjamin@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(original)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root path redirects to static HTML"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_success(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        
    def test_activities_structure(self, client):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
        
    def test_activities_initial_participants(self, client):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "emma@mergington.edu" in data["Programming Class"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
        
    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
        
    def test_signup_duplicate_participant(self, client):
        """Test that duplicate signup is rejected"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
        
    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multisport@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(f"/activities/Programming Class/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify in both
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Programming Class"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"
        
        # Verify participant is initially in the activity
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Chess Club"]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Chess Club"]["participants"]
        
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
        
    def test_unregister_not_registered(self, client):
        """Test unregistering a student who isn't registered returns 400"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
        
    def test_unregister_then_signup_again(self, client):
        """Test that a student can re-signup after unregistering"""
        email = "michael@mergington.edu"
        
        # Unregister
        response1 = client.delete(f"/activities/Chess Club/unregister?email={email}")
        assert response1.status_code == 200
        
        # Sign up again
        response2 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify back in the activity
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Chess Club"]["participants"]


class TestActivityCapacity:
    """Tests for activity capacity limits"""
    
    def test_activity_has_max_participants(self, client):
        """Test that activities have max_participants defined"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "max_participants" in activity_data
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0


class TestIntegrationScenarios:
    """Integration tests for realistic user scenarios"""
    
    def test_full_activity_lifecycle(self, client):
        """Test complete lifecycle: view, signup, unregister"""
        email = "testuser@mergington.edu"
        activity = "Chess Club"
        
        # 1. Get initial activities
        response1 = client.get("/activities")
        assert response1.status_code == 200
        initial_count = len(response1.json()[activity]["participants"])
        
        # 2. Sign up
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == 200
        
        # 3. Verify signup
        response3 = client.get("/activities")
        assert len(response3.json()[activity]["participants"]) == initial_count + 1
        assert email in response3.json()[activity]["participants"]
        
        # 4. Unregister
        response4 = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response4.status_code == 200
        
        # 5. Verify unregister
        response5 = client.get("/activities")
        assert len(response5.json()[activity]["participants"]) == initial_count
        assert email not in response5.json()[activity]["participants"]
