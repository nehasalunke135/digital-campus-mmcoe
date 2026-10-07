from rest_framework import serializers
from django.utils import timezone
from .models import (
    Internship,
    Hackathon,
    Application,
    HackathonRegistration,
    SavedOpportunity,
    OpportunityStatus,
    WorkMode,
    SavedContentType,
)
from .utils import is_closing_soon


class InternshipSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source="created_by.get_full_name")
    is_closing_soon = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    is_applied = serializers.SerializerMethodField()

    class Meta:
        model = Internship
        fields = [
            "id",
            "company_name",
            "company_logo",
            "role_title",
            "description",
            "location",
            "work_mode",
            "duration",
            "stipend",
            "eligibility",
            "eligible_branches",
            "eligible_years",
            "required_skills",
            "deadline",
            "application_url",
            "status",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "is_closing_soon",
            "is_saved",
            "is_applied",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_by",
            "created_at",
            "updated_at",
            "is_closing_soon",
            "is_saved",
            "is_applied",
        ]

    def get_is_closing_soon(self, obj):
        return is_closing_soon(obj.deadline)

    def get_is_saved(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated and getattr(request.user, "role", None) == "STUDENT":
            return SavedOpportunity.objects.filter(
                student=request.user,
                content_type=SavedContentType.INTERNSHIP,
                object_id=obj.id,
            ).exists()
        return False

    def get_is_applied(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated and getattr(request.user, "role", None) == "STUDENT":
            return Application.objects.filter(
                student=request.user,
                internship=obj,
            ).exists()
        return False

    def validate_company_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Company name cannot be empty.")
        return value.strip()

    def validate_role_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Role title cannot be empty.")
        return value.strip()

    def validate_description(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Description cannot be empty.")
        return value.strip()

    def validate_deadline(self, value):
        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.get_current_timezone())
        return value

    def create(self, validated_data):
        # HARD RULE: Status is ALWAYS forced to PENDING on creation
        validated_data["status"] = OpportunityStatus.PENDING
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Cannot change status directly via standard update
        validated_data.pop("status", None)
        validated_data.pop("created_by", None)
        return super().update(instance, validated_data)


class HackathonSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source="created_by.get_full_name")
    is_closing_soon = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    is_registered = serializers.SerializerMethodField()

    class Meta:
        model = Hackathon
        fields = [
            "id",
            "name",
            "organizer",
            "description",
            "location",
            "mode",
            "registration_deadline",
            "event_date",
            "team_size",
            "prize_pool",
            "eligibility",
            "required_skills_themes",
            "registration_url",
            "status",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "is_closing_soon",
            "is_saved",
            "is_registered",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_by",
            "created_at",
            "updated_at",
            "is_closing_soon",
            "is_saved",
            "is_registered",
        ]

    def get_is_closing_soon(self, obj):
        return is_closing_soon(obj.registration_deadline)

    def get_is_saved(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated and getattr(request.user, "role", None) == "STUDENT":
            return SavedOpportunity.objects.filter(
                student=request.user,
                content_type=SavedContentType.HACKATHON,
                object_id=obj.id,
            ).exists()
        return False

    def get_is_registered(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated and getattr(request.user, "role", None) == "STUDENT":
            return HackathonRegistration.objects.filter(
                student=request.user,
                hackathon=obj,
            ).exists()
        return False

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Hackathon name cannot be empty.")
        return value.strip()

    def validate_organizer(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Organizer cannot be empty.")
        return value.strip()

    def validate_description(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Description cannot be empty.")
        return value.strip()

    def validate(self, attrs):
        reg_deadline = attrs.get("registration_deadline", getattr(self.instance, "registration_deadline", None))
        event_date = attrs.get("event_date", getattr(self.instance, "event_date", None))
        if reg_deadline and event_date:
            if event_date < reg_deadline:
                raise serializers.ValidationError(
                    {"event_date": "Event date must be on or after the registration deadline."}
                )
        return attrs

    def create(self, validated_data):
        # HARD RULE: Status is ALWAYS forced to PENDING on creation
        validated_data["status"] = OpportunityStatus.PENDING
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("status", None)
        validated_data.pop("created_by", None)
        return super().update(instance, validated_data)


class ApplicationSerializer(serializers.ModelSerializer):
    internship = InternshipSerializer(read_only=True)
    internship_id = serializers.PrimaryKeyRelatedField(
        queryset=Internship.objects.all(), source="internship", write_only=True
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "student",
            "internship",
            "internship_id",
            "status",
            "initiated_at",
        ]
        read_only_fields = ["id", "student", "status", "initiated_at"]


class HackathonRegistrationSerializer(serializers.ModelSerializer):
    hackathon = HackathonSerializer(read_only=True)
    hackathon_id = serializers.PrimaryKeyRelatedField(
        queryset=Hackathon.objects.all(), source="hackathon", write_only=True
    )

    class Meta:
        model = HackathonRegistration
        fields = [
            "id",
            "student",
            "hackathon",
            "hackathon_id",
            "status",
            "initiated_at",
        ]
        read_only_fields = ["id", "student", "status", "initiated_at"]


class SavedOpportunitySerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()

    class Meta:
        model = SavedOpportunity
        fields = [
            "id",
            "student",
            "content_type",
            "object_id",
            "saved_at",
            "opportunity",
        ]
        read_only_fields = ["id", "student", "saved_at", "opportunity"]

    def get_opportunity(self, obj):
        request = self.context.get("request")
        if obj.content_type == SavedContentType.INTERNSHIP:
            try:
                item = Internship.objects.get(id=obj.object_id)
                return InternshipSerializer(item, context={"request": request}).data
            except Internship.DoesNotExist:
                return None
        elif obj.content_type == SavedContentType.HACKATHON:
            try:
                item = Hackathon.objects.get(id=obj.object_id)
                return HackathonSerializer(item, context={"request": request}).data
            except Hackathon.DoesNotExist:
                return None
        return None
