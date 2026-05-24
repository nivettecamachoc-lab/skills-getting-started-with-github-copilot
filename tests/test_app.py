"""
Backend API tests using FastAPI TestClient and AAA (Arrange-Act-Assert) pattern.
Each test clearly separates setup, execution, and verification phases.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """Reset activities to a known state before each test"""
    original_activities = {
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
        }
    }
    
    # Clear and repopulate activities
    activities.clear()
    activities.update(original_activities)
    
    yield activities
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client, fresh_activities):
        """
        Arrange: No setup needed
        Act: Call GET /activities
        Assert: Response status is 200
        """
        # Arrange
        # (no setup needed)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client, fresh_activities):
        """
        Arrange: No setup needed
        Act: Call GET /activities
        Assert: Response is a dictionary
        """
        # Arrange
        # (no setup needed)
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert isinstance(data, dict)
    
    def test_get_activities_contains_expected_activities(self, client, fresh_activities):
        """
        Arrange: Activities are already populated in fixture
        Act: Call GET /activities
        Assert: Response contains expected activity names
        """
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity in expected_activities:
            assert activity in data
    
    def test_get_activities_has_required_fields(self, client, fresh_activities):
        """
        Arrange: No setup needed
        Act: Call GET /activities
        Assert: Each activity has required fields
        """
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_returns_200(self, client, fresh_activities):
        """
        Arrange: Prepare new student email
        Act: POST signup request
        Assert: Response status is 200
        """
        # Arrange
        new_student = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": new_student}
        )
        
        # Assert
        assert response.status_code == 200
    
    def test_signup_new_student_returns_success_message(self, client, fresh_activities):
        """
        Arrange: Prepare new student email
        Act: POST signup request
        Assert: Response contains success message with student email
        """
        # Arrange
        new_student = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": new_student}
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert new_student in data["message"]
        assert "Signed up" in data["message"]
    
    def test_signup_adds_student_to_participants(self, client, fresh_activities):
        """
        Arrange: Prepare new student email
        Act: POST signup request, then fetch activities
        Assert: Student appears in participants list
        """
        # Arrange
        new_student = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Act
        client.post(
            f"/activities/{activity}/signup",
            params={"email": new_student}
        )
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert new_student in data[activity]["participants"]
    
    def test_signup_duplicate_student_returns_400(self, client, fresh_activities):
        """
        Arrange: Use already registered student
        Act: POST signup request with duplicate email
        Assert: Response status is 400
        """
        # Arrange
        existing_student = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": existing_student}
        )
        
        # Assert
        assert response.status_code == 400
    
    def test_signup_duplicate_student_error_message(self, client, fresh_activities):
        """
        Arrange: Use already registered student
        Act: POST signup request with duplicate email
        Assert: Error message indicates student already signed up
        """
        # Arrange
        existing_student = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": existing_student}
        )
        data = response.json()
        
        # Assert
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_returns_404(self, client, fresh_activities):
        """
        Arrange: Prepare nonexistent activity name
        Act: POST signup request for nonexistent activity
        Assert: Response status is 404
        """
        # Arrange
        activity = "Nonexistent Activity"
        student = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": student}
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_signup_nonexistent_activity_error_message(self, client, fresh_activities):
        """
        Arrange: Prepare nonexistent activity name
        Act: POST signup request for nonexistent activity
        Assert: Error message indicates activity not found
        """
        # Arrange
        activity = "Nonexistent Activity"
        student = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": student}
        )
        data = response.json()
        
        # Assert
        assert "not found" in data["detail"]


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_registered_student_returns_200(self, client, fresh_activities):
        """
        Arrange: Use registered student
        Act: POST unregister request
        Assert: Response status is 200
        """
        # Arrange
        student = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": student}
        )
        
        # Assert
        assert response.status_code == 200
    
    def test_unregister_registered_student_returns_message(self, client, fresh_activities):
        """
        Arrange: Use registered student
        Act: POST unregister request
        Assert: Response contains confirmation message
        """
        # Arrange
        student = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": student}
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert student in data["message"]
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_student_from_participants(self, client, fresh_activities):
        """
        Arrange: Use registered student
        Act: POST unregister request, then fetch activities
        Assert: Student no longer appears in participants list
        """
        # Arrange
        student = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act
        client.post(
            f"/activities/{activity}/unregister",
            params={"email": student}
        )
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert student not in data[activity]["participants"]
    
    def test_unregister_nonregistered_student_returns_400(self, client, fresh_activities):
        """
        Arrange: Use non-registered student email
        Act: POST unregister request
        Assert: Response status is 400
        """
        # Arrange
        student = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": student}
        )
        
        # Assert
        assert response.status_code == 400
    
    def test_unregister_nonregistered_student_error_message(self, client, fresh_activities):
        """
        Arrange: Use non-registered student email
        Act: POST unregister request
        Assert: Error message indicates student not registered
        """
        # Arrange
        student = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": student}
        )
        data = response.json()
        
        # Assert
        assert "not registered" in data["detail"]
    
    def test_unregister_nonexistent_activity_returns_404(self, client, fresh_activities):
        """
        Arrange: Prepare nonexistent activity name
        Act: POST unregister request for nonexistent activity
        Assert: Response status is 404
        """
        # Arrange
        activity = "Nonexistent Activity"
        student = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": student}
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_unregister_nonexistent_activity_error_message(self, client, fresh_activities):
        """
        Arrange: Prepare nonexistent activity name
        Act: POST unregister request for nonexistent activity
        Assert: Error message indicates activity not found
        """
        # Arrange
        activity = "Nonexistent Activity"
        student = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": student}
        )
        data = response.json()
        
        # Assert
        assert "not found" in data["detail"]


class TestSignupAndUnregisterFlow:
    """Integration tests for signup and unregister flow"""
    
    def test_complete_signup_and_unregister_flow(self, client, fresh_activities):
        """
        Arrange: Prepare new student and activity
        Act: Sign up, verify, unregister, verify again
        Assert: All operations succeed and participant list updates correctly
        """
        # Arrange
        student = "flowtest@mergington.edu"
        activity = "Chess Club"
        initial_count = len(activities[activity]["participants"])
        
        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": student}
        )
        assert signup_response.status_code == 200
        
        # Assert - Signup increased count
        get_response = client.get("/activities")
        data = get_response.json()
        assert student in data[activity]["participants"]
        assert len(data[activity]["participants"]) == initial_count + 1
        
        # Act - Unregister
        unregister_response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": student}
        )
        assert unregister_response.status_code == 200
        
        # Assert - Unregister restored count
        get_response = client.get("/activities")
        data = get_response.json()
        assert student not in data[activity]["participants"]
        assert len(data[activity]["participants"]) == initial_count
    
    def test_signup_then_duplicate_signup_fails(self, client, fresh_activities):
        """
        Arrange: Prepare new student email
        Act: First signup succeeds, second signup attempted
        Assert: First succeeds (200), second fails (400)
        """
        # Arrange
        student = "duplicate@mergington.edu"
        activity = "Chess Club"
        
        # Act - First signup
        first_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": student}
        )
        
        # Assert - First signup succeeds
        assert first_response.status_code == 200
        
        # Act - Second signup
        second_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": student}
        )
        
        # Assert - Second signup fails
        assert second_response.status_code == 400
        assert "already signed up" in second_response.json()["detail"]
    
    def test_unregister_then_signup_again(self, client, fresh_activities):
        """
        Arrange: Prepare student and activity
        Act: Sign up, unregister, sign up again
        Assert: All operations succeed
        """
        # Arrange
        student = "resign@mergington.edu"
        activity = "Chess Club"
        
        # Act - First signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": student}
        )
        
        # Assert - First signup succeeds
        assert response1.status_code == 200
        
        # Act - Unregister
        response2 = client.post(
            f"/activities/{activity}/unregister",
            params={"email": student}
        )
        
        # Assert - Unregister succeeds
        assert response2.status_code == 200
        
        # Act - Sign up again
        response3 = client.post(
            f"/activities/{activity}/signup",
            params={"email": student}
        )
        
        # Assert - Second signup succeeds
        assert response3.status_code == 200
