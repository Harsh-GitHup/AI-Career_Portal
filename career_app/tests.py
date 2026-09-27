from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from career_app.models import Opportunity, ProfileMatch, StudentProfile


class CareerAppTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.profile = StudentProfile.objects.create(
            user=self.user,
            target_role="Software Engineer",
            current_skills=["Python", "Django"],
        )

        self.opportunity = Opportunity.objects.create(
            dedupe_hash="opp1",
            title="Django Developer",
            provider="TechCorp",
            opportunity_type="Job",
            is_free=True,
            url="http://example.com/job1",
        )
        ProfileMatch.objects.create(
            profile=self.profile, opportunity=self.opportunity, relevance_score=85.0
        )

    def test_login_api(self):
        response = self.client.post(
            "/api/login/",
            {"username": "testuser", "password": "testpassword"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user_id", response.data)

    def test_register_api(self):
        response = self.client.post(
            "/api/register/",
            {"username": "newuser", "password": "newpassword", "email": "new@test.com"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_opportunities_list(self):
        response = self.client.get("/api/opportunities/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_recommendations_api(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/recommendations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("opportunities", response.data)
        self.assertEqual(len(response.data["opportunities"]), 1)

    def test_profile_unauthenticated(self):
        # Should block access to profiles without auth
        response = self.client.get("/api/profiles/")
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_toggle_bookmark(self):
        self.client.force_authenticate(user=self.user)
        match = ProfileMatch.objects.first()
        response = self.client.post(f"/api/bookmark/{match.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_bookmarked"])

    def test_social_login_invalid_token(self):
        response = self.client.post(
            "/api/social-login/", {"token": "invalid_token"}, format="json"
        )
        # Google Auth will throw ValueError for 'invalid_token'
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("career_app.views.analyze_resume")
    @patch("career_app.tasks.run_universal_scraper.delay")
    def test_upload_resume_api(self, mock_scraper, mock_analyze):
        # Mock analysis result
        class MockAnalysis:
            full_name = "Jane Doe"
            target_professions = ["Data Scientist"]
            extracted_skills = ["Python"]
            skill_gaps = []
            recommended_courses = []
            resume_improvements = []
            interview_questions = []

        mock_analyze.return_value = MockAnalysis()

        self.client.force_authenticate(user=self.user)
        # We simulate a PDF file upload
        from django.core.files.uploadedfile import SimpleUploadedFile

        pdf = SimpleUploadedFile(
            "resume.pdf", b"file_content", content_type="application/pdf"
        )

        response = self.client.post(
            "/api/upload-resume/", {"resume": pdf}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["full_name"], "Jane Doe")
        self.assertEqual(response.data["target_role"], "Data Scientist")
