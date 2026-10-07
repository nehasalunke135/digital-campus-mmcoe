from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from core_auth.models import User, UserRole
from interx.models import (
    Internship,
    Hackathon,
    Application,
    HackathonRegistration,
    SavedOpportunity,
    OpportunityStatus,
    WorkMode,
    ApplicationStatus,
    SavedContentType,
)


class InterXBackendTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create Admin
        self.admin = User.objects.create_user(
            username="admin@mmcoe.edu.in",
            email="admin@mmcoe.edu.in",
            password="Admin@123",
            role=UserRole.ADMIN,
            full_name="Admin Officer",
        )

        # Create Student A
        self.student_a = User.objects.create_user(
            username="student.a@mmcoe.edu.in",
            email="student.a@mmcoe.edu.in",
            password="Student@123",
            role=UserRole.STUDENT,
            full_name="Student A",
        )

        # Create Student B
        self.student_b = User.objects.create_user(
            username="student.b@mmcoe.edu.in",
            email="student.b@mmcoe.edu.in",
            password="Student@123",
            role=UserRole.STUDENT,
            full_name="Student B",
        )

        now = timezone.now()

        # Seed 1 Published Internship
        self.published_internship = Internship.objects.create(
            company_name="Infosys",
            role_title="Software Intern",
            description="Infosys Internship Program",
            location="Pune",
            work_mode=WorkMode.HYBRID,
            duration="3 months",
            deadline=now + timedelta(days=10),
            application_url="https://infosys.com/careers",
            status=OpportunityStatus.PUBLISHED,
            created_by=self.admin,
        )

        # Seed 1 Pending Internship
        self.pending_internship = Internship.objects.create(
            company_name="Wipro",
            role_title="QA Intern",
            description="Wipro Internship Program",
            location="Pune",
            work_mode=WorkMode.ONSITE,
            duration="6 months",
            deadline=now + timedelta(days=15),
            application_url="https://wipro.com/careers",
            status=OpportunityStatus.PENDING,
            created_by=self.admin,
        )

        # Seed 1 Published Hackathon
        self.published_hackathon = Hackathon.objects.create(
            name="MMCOE HackFest 2026",
            organizer="MMCOE ACM Chapter",
            description="Annual Intra-college Hackathon",
            location="MMCOE Campus",
            mode=WorkMode.ONSITE,
            registration_deadline=now + timedelta(days=5),
            event_date=now + timedelta(days=10),
            registration_url="https://mmcoe.edu.in/hackfest",
            status=OpportunityStatus.PUBLISHED,
            created_by=self.admin,
        )

    # 1. Opportunity Status Lifecycle & Constraints
    def test_creation_forces_pending_status(self):
        """Even if client sends status=PUBLISHED, creation must force PENDING"""
        self.client.force_authenticate(user=self.admin)
        payload = {
            "company_name": "Persistent",
            "role_title": "Backend Intern",
            "description": "Django Backend Role",
            "location": "Pune",
            "work_mode": "REMOTE",
            "duration": "3 months",
            "deadline": (timezone.now() + timedelta(days=10)).isoformat(),
            "application_url": "https://persistent.com/apply",
            "status": "PUBLISHED",  # Client attempts to bypass review
        }
        response = self.client.post("/api/interx/internships/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "PENDING")

    def test_admin_publish_transition(self):
        """Admin publishes PENDING -> PUBLISHED"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f"/api/interx/internships/{self.pending_internship.id}/publish/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pending_internship.refresh_from_db()
        self.assertEqual(self.pending_internship.status, OpportunityStatus.PUBLISHED)

    def test_admin_edit_pending_remains_pending(self):
        """Admin edits PENDING -> remains PENDING"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"/api/interx/internships/{self.pending_internship.id}/",
            {"role_title": "Senior QA Intern"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pending_internship.refresh_from_db()
        self.assertEqual(self.pending_internship.role_title, "Senior QA Intern")
        self.assertEqual(self.pending_internship.status, OpportunityStatus.PENDING)

    def test_admin_close_published(self):
        """Admin closes PUBLISHED -> CLOSED"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f"/api/interx/internships/{self.published_internship.id}/close/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.published_internship.refresh_from_db()
        self.assertEqual(self.published_internship.status, OpportunityStatus.CLOSED)

    def test_admin_remove_opportunity(self):
        """Admin removes opportunity (deleted from DB)"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f"/api/interx/internships/{self.pending_internship.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Internship.objects.filter(id=self.pending_internship.id).exists())

    # 2. Role Permissions & Security Boundary
    def test_student_cannot_create_internship(self):
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(
            "/api/interx/internships/",
            {
                "company_name": "Test",
                "role_title": "Test",
                "description": "Test",
                "location": "Pune",
                "work_mode": "ONSITE",
                "duration": "1 month",
                "deadline": (timezone.now() + timedelta(days=5)).isoformat(),
                "application_url": "https://test.com",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "FORBIDDEN")

    def test_student_cannot_publish_internship(self):
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(f"/api/interx/internships/{self.pending_internship.id}/publish/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "FORBIDDEN")

    def test_student_cannot_delete_internship(self):
        self.client.force_authenticate(user=self.student_a)
        response = self.client.delete(f"/api/interx/internships/{self.published_internship.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_see_pending_internships(self):
        self.client.force_authenticate(user=self.student_a)
        response = self.client.get("/api/interx/internships/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data]
        self.assertIn(self.published_internship.id, ids)
        self.assertNotIn(self.pending_internship.id, ids)

        # Direct detail access by student should return 403
        detail_response = self.client.get(f"/api/interx/internships/{self.pending_internship.id}/")
        self.assertEqual(detail_response.status_code, status.HTTP_403_FORBIDDEN)

    # 3. Student Personal Data Isolation
    def test_student_data_isolation(self):
        """Student A actions are private and never visible to Student B"""
        self.client.force_authenticate(user=self.student_a)

        # Student A applies to internship
        apply_res = self.client.post(f"/api/interx/internships/{self.published_internship.id}/apply/")
        self.assertEqual(apply_res.status_code, status.HTTP_200_OK)
        self.assertEqual(apply_res.data["status"], "INITIATED")
        self.assertEqual(apply_res.data["redirect_url"], self.published_internship.application_url)

        # Student A saves hackathon
        save_res = self.client.post(f"/api/interx/hackathons/{self.published_hackathon.id}/save/")
        self.assertEqual(save_res.status_code, status.HTTP_201_CREATED)

        # Check Student A's personal endpoints
        apps_a = self.client.get("/api/interx/my/applications/")
        self.assertEqual(len(apps_a.data), 1)

        saved_a = self.client.get("/api/interx/my/saved/")
        self.assertEqual(len(saved_a.data), 1)

        # Now authenticate as Student B
        self.client.force_authenticate(user=self.student_b)

        # Student B must see 0 applications and 0 saved
        apps_b = self.client.get("/api/interx/my/applications/")
        self.assertEqual(len(apps_b.data), 0)

        saved_b = self.client.get("/api/interx/my/saved/")
        self.assertEqual(len(saved_b.data), 0)

    # 4. Expiry Handling
    def test_expired_opportunity_blocks_application(self):
        """Past deadline transitions to EXPIRED and blocks apply"""
        now = timezone.now()
        expired_internship = Internship.objects.create(
            company_name="Old Corp",
            role_title="Old Intern",
            description="Past deadline role",
            location="Pune",
            work_mode=WorkMode.ONSITE,
            duration="1 month",
            deadline=now - timedelta(days=2),
            application_url="https://oldcorp.com",
            status=OpportunityStatus.PUBLISHED,
            created_by=self.admin,
        )

        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(f"/api/interx/internships/{expired_internship.id}/apply/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "VALIDATION_ERROR")

    # 5. Standard Error Format
    def test_error_schema_format(self):
        self.client.force_authenticate(user=self.student_a)
        # Attempt an invalid operation to trigger error
        response = self.client.get("/api/interx/internships/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)
        self.assertIn("message", response.data)
        self.assertIn("field_errors", response.data)
