from django.urls import path
from .views import (
    InternshipListCreateView,
    InternshipDetailView,
    InternshipPublishView,
    InternshipCloseView,
    InternshipApplyView,
    InternshipSaveView,
    HackathonListCreateView,
    HackathonDetailView,
    HackathonPublishView,
    HackathonCloseView,
    HackathonRegisterView,
    HackathonSaveView,
    MyApplicationsView,
    MyRegistrationsView,
    MySavedOpportunitiesView,
    AdminDashboardView,
)

urlpatterns = [
    # Internships
    path("internships/", InternshipListCreateView.as_view(), name="internship-list-create"),
    path("internships/<int:pk>/", InternshipDetailView.as_view(), name="internship-detail"),
    path("internships/<int:pk>/publish/", InternshipPublishView.as_view(), name="internship-publish"),
    path("internships/<int:pk>/close/", InternshipCloseView.as_view(), name="internship-close"),
    path("internships/<int:pk>/apply/", InternshipApplyView.as_view(), name="internship-apply"),
    path("internships/<int:pk>/save/", InternshipSaveView.as_view(), name="internship-save"),

    # Hackathons
    path("hackathons/", HackathonListCreateView.as_view(), name="hackathon-list-create"),
    path("hackathons/<int:pk>/", HackathonDetailView.as_view(), name="hackathon-detail"),
    path("hackathons/<int:pk>/publish/", HackathonPublishView.as_view(), name="hackathon-publish"),
    path("hackathons/<int:pk>/close/", HackathonCloseView.as_view(), name="hackathon-close"),
    path("hackathons/<int:pk>/register/", HackathonRegisterView.as_view(), name="hackathon-register"),
    path("hackathons/<int:pk>/save/", HackathonSaveView.as_view(), name="hackathon-save"),

    # Student personal data
    path("my/applications/", MyApplicationsView.as_view(), name="my-applications"),
    path("my/registrations/", MyRegistrationsView.as_view(), name="my-registrations"),
    path("my/saved/", MySavedOpportunitiesView.as_view(), name="my-saved"),

    # Admin dashboard
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
]
