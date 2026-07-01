import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Should return all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_includes_participant_info(self, client):
        """Should include participant information for each activity"""
        response = client.get("/activities")
        data = response.json()
        chess = data["Chess Club"]
        assert "participants" in chess
        assert "max_participants" in chess
        assert len(chess["participants"]) == 2
        assert "michael@mergington.edu" in chess["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client):
        """Should successfully add a new participant"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "newstudent@mergington.edu" in data["message"]

        # Verify participant was added
        activities_response = client.get("/activities")
        chess = activities_response.json()["Chess Club"]
        assert "newstudent@mergington.edu" in chess["participants"]
        assert len(chess["participants"]) == 3

    def test_signup_duplicate_email_fails(self, client):
        """Should fail when student tries to sign up twice"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self, client):
        """Should fail when activity doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_multiple_different_students(self, client):
        """Should allow multiple different students to sign up"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        for email in emails:
            response = client.post(f"/activities/Gym Class/signup?email={email}")
            assert response.status_code == 200

        # Verify all were added
        activities_response = client.get("/activities")
        gym = activities_response.json()["Gym Class"]
        for email in emails:
            assert email in gym["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, client):
        """Should successfully remove a participant"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "michael@mergington.edu" in data["message"]

        # Verify participant was removed
        activities_response = client.get("/activities")
        chess = activities_response.json()["Chess Club"]
        assert "michael@mergington.edu" not in chess["participants"]
        assert len(chess["participants"]) == 1

    def test_unregister_nonexistent_participant_fails(self, client):
        """Should fail when trying to unregister someone not signed up"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_nonexistent_activity_fails(self, client):
        """Should fail when activity doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_all_participants(self, client):
        """Should allow unregistering all participants"""
        activity = "Programming Class"
        participants = ["emma@mergington.edu", "sophia@mergington.edu"]

        for email in participants:
            response = client.delete(
                f"/activities/{activity}/unregister?email={email}"
            )
            assert response.status_code == 200

        # Verify all were removed
        activities_response = client.get("/activities")
        prog = activities_response.json()[activity]
        assert len(prog["participants"]) == 0
