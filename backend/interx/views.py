from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Internship,
    Hackathon,
    Application,
    HackathonRegistration,
    SavedOpportunity,
    OpportunityStatus,
    SavedContentType,
    ApplicationStatus,
)
from .permissions import IsAdminRole, IsStudentRole, IsAdminOrStudentReadOnly
from .serializers import (
    InternshipSerializer,
    HackathonSerializer,
    ApplicationSerializer,
    HackathonRegistrationSerializer,
    SavedOpportunitySerializer,
)
from .utils import update_expired_opportunities


class InternshipListCreateView(APIView):
    permission_classes = [IsAdminOrStudentReadOnly]

    def get(self, request):
        update_expired_opportunities()
        user = request.user
        queryset = Internship.objects.all()

        if getattr(user, "role", None) != "ADMIN":
            # Hard CDD Rule: Students see only PUBLISHED and not expired
            queryset = queryset.filter(status=OpportunityStatus.PUBLISHED)
        else:
            status_param = request.query_params.get("status")
            if status_param:
                queryset = queryset.filter(status=status_param.upper())

        # Filtering
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(company_name__icontains=search)
                | Q(role_title__icontains=search)
                | Q(description__icontains=search)
            )

        work_mode = request.query_params.get("work_mode")
        if work_mode:
            queryset = queryset.filter(work_mode=work_mode.upper())

        location = request.query_params.get("location")
        if location:
            queryset = queryset.filter(location__icontains=location)

        branch = request.query_params.get("branch")
        if branch:
            queryset = queryset.filter(eligible_branches__icontains=branch)

        year = request.query_params.get("year")
        if year:
            try:
                year_int = int(year)
                queryset = queryset.filter(eligible_years__contains=[year_int])
            except ValueError:
                pass

        skill = request.query_params.get("skill")
        if skill:
            queryset = queryset.filter(required_skills__icontains=skill)

        ordering = request.query_params.get("ordering", "-created_at")
        if ordering in ["deadline", "-deadline", "created_at", "-created_at"]:
            queryset = queryset.order_by(ordering)

        serializer = InternshipSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        if getattr(request.user, "role", None) != "ADMIN":
            raise PermissionDenied("Only administrators can add internships.")

        serializer = InternshipSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        internship = serializer.save()
        return Response(
            InternshipSerializer(internship, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class InternshipDetailView(APIView):
    permission_classes = [IsAdminOrStudentReadOnly]

    def get_object(self, pk, user):
        update_expired_opportunities()
        try:
            internship = Internship.objects.get(pk=pk)
        except Internship.DoesNotExist:
            raise NotFound("Internship not found.")

        # Hard CDD rule: Students only if PUBLISHED
        if getattr(user, "role", None) != "ADMIN" and internship.status != OpportunityStatus.PUBLISHED:
            raise PermissionDenied("You do not have permission to view this unpublished opportunity.")

        return internship

    def get(self, request, pk):
        internship = self.get_object(pk, request.user)
        serializer = InternshipSerializer(internship, context={"request": request})
        return Response(serializer.data)

    def patch(self, request, pk):
        if getattr(request.user, "role", None) != "ADMIN":
            raise PermissionDenied("Only administrators can edit internships.")

        internship = self.get_object(pk, request.user)
        serializer = InternshipSerializer(
            internship,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return Response(InternshipSerializer(updated, context={"request": request}).data)

    def delete(self, request, pk):
        if getattr(request.user, "role", None) != "ADMIN":
            raise PermissionDenied("Only administrators can remove internships.")

        internship = self.get_object(pk, request.user)
        internship.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InternshipPublishView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        update_expired_opportunities()
        try:
            internship = Internship.objects.get(pk=pk)
        except Internship.DoesNotExist:
            raise NotFound("Internship not found.")

        # Allowed transition: PENDING -> PUBLISHED
        if internship.status != OpportunityStatus.PENDING:
            raise ValidationError(
                {"status": f"Cannot publish internship with status {internship.status}. Only PENDING items can be published."}
            )

        if internship.deadline <= timezone.now():
            raise ValidationError({"deadline": "Cannot publish an internship whose deadline has already passed."})

        internship.status = OpportunityStatus.PUBLISHED
        internship.save()
        return Response(InternshipSerializer(internship, context={"request": request}).data)


class InternshipCloseView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            internship = Internship.objects.get(pk=pk)
        except Internship.DoesNotExist:
            raise NotFound("Internship not found.")

        # Allowed transition: PUBLISHED -> CLOSED
        if internship.status != OpportunityStatus.PUBLISHED:
            raise ValidationError(
                {"status": f"Cannot close internship with status {internship.status}. Only PUBLISHED items can be closed."}
            )

        internship.status = OpportunityStatus.CLOSED
        internship.save()
        return Response(InternshipSerializer(internship, context={"request": request}).data)


class InternshipApplyView(APIView):
    permission_classes = [IsStudentRole]

    def post(self, request, pk):
        update_expired_opportunities()
        try:
            internship = Internship.objects.get(pk=pk)
        except Internship.DoesNotExist:
            raise NotFound("Internship not found.")

        if internship.status == OpportunityStatus.EXPIRED or internship.deadline <= timezone.now():
            raise ValidationError({"deadline": "This internship deadline has passed (EXPIRED)."})

        if internship.status != OpportunityStatus.PUBLISHED:
            raise PermissionDenied("Cannot apply to an unpublished internship.")

        application, created = Application.objects.update_or_create(
            student=request.user,
            internship=internship,
            defaults={"status": ApplicationStatus.INITIATED},
        )

        return Response(
            {
                "application_id": application.id,
                "internship_id": internship.id,
                "status": application.status,
                "redirect_url": internship.application_url,
                "initiated_at": application.initiated_at,
            },
            status=status.HTTP_200_OK,
        )


class InternshipSaveView(APIView):
    permission_classes = [IsStudentRole]

    def post(self, request, pk):
        update_expired_opportunities()
        try:
            internship = Internship.objects.get(pk=pk)
        except Internship.DoesNotExist:
            raise NotFound("Internship not found.")

        if internship.status == OpportunityStatus.EXPIRED or internship.deadline <= timezone.now():
            raise ValidationError({"deadline": "Cannot save an expired opportunity."})

        if internship.status != OpportunityStatus.PUBLISHED:
            raise PermissionDenied("Cannot save an unpublished opportunity.")

        saved, _ = SavedOpportunity.objects.get_or_create(
            student=request.user,
            content_type=SavedContentType.INTERNSHIP,
            object_id=internship.id,
        )
        return Response(
            {"message": "Internship saved successfully.", "id": saved.id},
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, pk):
        deleted_count, _ = SavedOpportunity.objects.filter(
            student=request.user,
            content_type=SavedContentType.INTERNSHIP,
            object_id=pk,
        ).delete()

        if deleted_count == 0:
            raise NotFound("Saved opportunity not found.")

        return Response(
            {"message": "Internship removed from saved list."},
            status=status.HTTP_200_OK,
        )


# --- HACKATHONS ---

class HackathonListCreateView(APIView):
    permission_classes = [IsAdminOrStudentReadOnly]

    def get(self, request):
        update_expired_opportunities()
        user = request.user
        queryset = Hackathon.objects.all()

        if getattr(user, "role", None) != "ADMIN":
            queryset = queryset.filter(status=OpportunityStatus.PUBLISHED)
        else:
            status_param = request.query_params.get("status")
            if status_param:
                queryset = queryset.filter(status=status_param.upper())

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(organizer__icontains=search)
                | Q(description__icontains=search)
            )

        mode = request.query_params.get("work_mode") or request.query_params.get("mode")
        if mode:
            queryset = queryset.filter(mode=mode.upper())

        location = request.query_params.get("location")
        if location:
            queryset = queryset.filter(location__icontains=location)

        skill = request.query_params.get("skill")
        if skill:
            queryset = queryset.filter(required_skills_themes__icontains=skill)

        ordering = request.query_params.get("ordering", "-created_at")
        if ordering in ["registration_deadline", "-registration_deadline", "event_date", "-event_date", "created_at", "-created_at"]:
            queryset = queryset.order_by(ordering)

        serializer = HackathonSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        if getattr(request.user, "role", None) != "ADMIN":
            raise PermissionDenied("Only administrators can add hackathons.")

        serializer = HackathonSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        hackathon = serializer.save()
        return Response(
            HackathonSerializer(hackathon, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class HackathonDetailView(APIView):
    permission_classes = [IsAdminOrStudentReadOnly]

    def get_object(self, pk, user):
        update_expired_opportunities()
        try:
            hackathon = Hackathon.objects.get(pk=pk)
        except Hackathon.DoesNotExist:
            raise NotFound("Hackathon not found.")

        if getattr(user, "role", None) != "ADMIN" and hackathon.status != OpportunityStatus.PUBLISHED:
            raise PermissionDenied("You do not have permission to view this unpublished opportunity.")

        return hackathon

    def get(self, request, pk):
        hackathon = self.get_object(pk, request.user)
        serializer = HackathonSerializer(hackathon, context={"request": request})
        return Response(serializer.data)

    def patch(self, request, pk):
        if getattr(request.user, "role", None) != "ADMIN":
            raise PermissionDenied("Only administrators can edit hackathons.")

        hackathon = self.get_object(pk, request.user)
        serializer = HackathonSerializer(
            hackathon,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return Response(HackathonSerializer(updated, context={"request": request}).data)

    def delete(self, request, pk):
        if getattr(request.user, "role", None) != "ADMIN":
            raise PermissionDenied("Only administrators can remove hackathons.")

        hackathon = self.get_object(pk, request.user)
        hackathon.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HackathonPublishView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        update_expired_opportunities()
        try:
            hackathon = Hackathon.objects.get(pk=pk)
        except Hackathon.DoesNotExist:
            raise NotFound("Hackathon not found.")

        if hackathon.status != OpportunityStatus.PENDING:
            raise ValidationError(
                {"status": f"Cannot publish hackathon with status {hackathon.status}. Only PENDING items can be published."}
            )

        if hackathon.registration_deadline <= timezone.now():
            raise ValidationError({"registration_deadline": "Cannot publish a hackathon whose registration deadline has passed."})

        hackathon.status = OpportunityStatus.PUBLISHED
        hackathon.save()
        return Response(HackathonSerializer(hackathon, context={"request": request}).data)


class HackathonCloseView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            hackathon = Hackathon.objects.get(pk=pk)
        except Hackathon.DoesNotExist:
            raise NotFound("Hackathon not found.")

        if hackathon.status != OpportunityStatus.PUBLISHED:
            raise ValidationError(
                {"status": f"Cannot close hackathon with status {hackathon.status}. Only PUBLISHED items can be closed."}
            )

        hackathon.status = OpportunityStatus.CLOSED
        hackathon.save()
        return Response(HackathonSerializer(hackathon, context={"request": request}).data)


class HackathonRegisterView(APIView):
    permission_classes = [IsStudentRole]

    def post(self, request, pk):
        update_expired_opportunities()
        try:
            hackathon = Hackathon.objects.get(pk=pk)
        except Hackathon.DoesNotExist:
            raise NotFound("Hackathon not found.")

        if hackathon.status == OpportunityStatus.EXPIRED or hackathon.registration_deadline <= timezone.now():
            raise ValidationError({"registration_deadline": "This hackathon registration deadline has passed (EXPIRED)."})

        if hackathon.status != OpportunityStatus.PUBLISHED:
            raise PermissionDenied("Cannot register for an unpublished hackathon.")

        registration, created = HackathonRegistration.objects.update_or_create(
            student=request.user,
            hackathon=hackathon,
            defaults={"status": ApplicationStatus.INITIATED},
        )

        return Response(
            {
                "registration_id": registration.id,
                "hackathon_id": hackathon.id,
                "status": registration.status,
                "redirect_url": hackathon.registration_url,
                "initiated_at": registration.initiated_at,
            },
            status=status.HTTP_200_OK,
        )


class HackathonSaveView(APIView):
    permission_classes = [IsStudentRole]

    def post(self, request, pk):
        update_expired_opportunities()
        try:
            hackathon = Hackathon.objects.get(pk=pk)
        except Hackathon.DoesNotExist:
            raise NotFound("Hackathon not found.")

        if hackathon.status == OpportunityStatus.EXPIRED or hackathon.registration_deadline <= timezone.now():
            raise ValidationError({"registration_deadline": "Cannot save an expired opportunity."})

        if hackathon.status != OpportunityStatus.PUBLISHED:
            raise PermissionDenied("Cannot save an unpublished opportunity.")

        saved, _ = SavedOpportunity.objects.get_or_create(
            student=request.user,
            content_type=SavedContentType.HACKATHON,
            object_id=hackathon.id,
        )
        return Response(
            {"message": "Hackathon saved successfully.", "id": saved.id},
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, pk):
        deleted_count, _ = SavedOpportunity.objects.filter(
            student=request.user,
            content_type=SavedContentType.HACKATHON,
            object_id=pk,
        ).delete()

        if deleted_count == 0:
            raise NotFound("Saved opportunity not found.")

        return Response(
            {"message": "Hackathon removed from saved list."},
            status=status.HTTP_200_OK,
        )


# --- STUDENT PERSONAL APIS ---

class MyApplicationsView(APIView):
    permission_classes = [IsStudentRole]

    def get(self, request):
        # Strict scope to request.user
        applications = Application.objects.filter(student=request.user)
        serializer = ApplicationSerializer(applications, many=True, context={"request": request})
        return Response(serializer.data)


class MyRegistrationsView(APIView):
    permission_classes = [IsStudentRole]

    def get(self, request):
        # Strict scope to request.user
        registrations = HackathonRegistration.objects.filter(student=request.user)
        serializer = HackathonRegistrationSerializer(registrations, many=True, context={"request": request})
        return Response(serializer.data)


class MySavedOpportunitiesView(APIView):
    permission_classes = [IsStudentRole]

    def get(self, request):
        # Strict scope to request.user
        saved = SavedOpportunity.objects.filter(student=request.user)
        serializer = SavedOpportunitySerializer(saved, many=True, context={"request": request})
        return Response(serializer.data)


# --- ADMIN DASHBOARD API ---

class AdminDashboardView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        update_expired_opportunities()

        internships_total = Internship.objects.count()
        internships_pending = Internship.objects.filter(status=OpportunityStatus.PENDING).count()
        internships_published = Internship.objects.filter(status=OpportunityStatus.PUBLISHED).count()
        internships_expired = Internship.objects.filter(status=OpportunityStatus.EXPIRED).count()
        internships_closed = Internship.objects.filter(status=OpportunityStatus.CLOSED).count()

        hackathons_total = Hackathon.objects.count()
        hackathons_pending = Hackathon.objects.filter(status=OpportunityStatus.PENDING).count()
        hackathons_published = Hackathon.objects.filter(status=OpportunityStatus.PUBLISHED).count()
        hackathons_expired = Hackathon.objects.filter(status=OpportunityStatus.EXPIRED).count()
        hackathons_closed = Hackathon.objects.filter(status=OpportunityStatus.CLOSED).count()

        return Response(
            {
                "internships": {
                    "total": internships_total,
                    "pending": internships_pending,
                    "published": internships_published,
                    "expired": internships_expired,
                    "closed": internships_closed,
                },
                "hackathons": {
                    "total": hackathons_total,
                    "pending": hackathons_pending,
                    "published": hackathons_published,
                    "expired": hackathons_expired,
                    "closed": hackathons_closed,
                },
            }
        )
