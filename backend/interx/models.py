from django.conf import settings
from django.db import models


class OpportunityStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PUBLISHED = "PUBLISHED", "Published"
    EXPIRED = "EXPIRED", "Expired"
    CLOSED = "CLOSED", "Closed"


class WorkMode(models.TextChoices):
    ONSITE = "ONSITE", "Onsite"
    REMOTE = "REMOTE", "Remote"
    HYBRID = "HYBRID", "Hybrid"


class SavedContentType(models.TextChoices):
    INTERNSHIP = "INTERNSHIP", "Internship"
    HACKATHON = "HACKATHON", "Hackathon"


class ApplicationStatus(models.TextChoices):
    INITIATED = "INITIATED", "Initiated"


class Internship(models.Model):
    company_name = models.CharField(max_length=255)
    company_logo = models.URLField(blank=True, default="")
    role_title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    work_mode = models.CharField(max_length=20, choices=WorkMode.choices)
    duration = models.CharField(max_length=100)
    stipend = models.CharField(max_length=100, blank=True, default="")
    eligibility = models.TextField(blank=True, default="")
    eligible_branches = models.JSONField(default=list, blank=True)
    eligible_years = models.JSONField(default=list, blank=True)
    required_skills = models.JSONField(default=list, blank=True)
    deadline = models.DateTimeField()
    application_url = models.URLField()
    status = models.CharField(
        max_length=20,
        choices=OpportunityStatus.choices,
        default=OpportunityStatus.PENDING,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_internships",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.role_title} at {self.company_name} ({self.status})"


class Hackathon(models.Model):
    name = models.CharField(max_length=255)
    organizer = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    mode = models.CharField(max_length=20, choices=WorkMode.choices)
    registration_deadline = models.DateTimeField()
    event_date = models.DateTimeField()
    team_size = models.CharField(max_length=50, blank=True, default="")
    prize_pool = models.CharField(max_length=100, blank=True, default="")
    eligibility = models.TextField(blank=True, default="")
    required_skills_themes = models.JSONField(default=list, blank=True)
    registration_url = models.URLField()
    status = models.CharField(
        max_length=20,
        choices=OpportunityStatus.choices,
        default=OpportunityStatus.PENDING,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_hackathons",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} by {self.organizer} ({self.status})"


class Application(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="internship_applications",
    )
    internship = models.ForeignKey(
        Internship,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.INITIATED,
    )
    initiated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "internship"],
                name="unique_student_internship_application",
            )
        ]
        ordering = ["-initiated_at"]

    def __str__(self):
        return f"Student {self.student_id} -> Internship {self.internship_id} ({self.status})"


class HackathonRegistration(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hackathon_registrations",
    )
    hackathon = models.ForeignKey(
        Hackathon,
        on_delete=models.CASCADE,
        related_name="registrations",
    )
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.INITIATED,
    )
    initiated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "hackathon"],
                name="unique_student_hackathon_registration",
            )
        ]
        ordering = ["-initiated_at"]

    def __str__(self):
        return f"Student {self.student_id} -> Hackathon {self.hackathon_id} ({self.status})"


class SavedOpportunity(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_opportunities",
    )
    content_type = models.CharField(
        max_length=20,
        choices=SavedContentType.choices,
    )
    object_id = models.PositiveIntegerField()
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "content_type", "object_id"],
                name="unique_student_saved_opportunity",
            )
        ]
        ordering = ["-saved_at"]

    def __str__(self):
        return f"Student {self.student_id} saved {self.content_type} {self.object_id}"
