from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Common serialized representation of an authenticated user.
    """
    name = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'full_name',
            'first_name',
            'last_name',
            'name',
            'role',
            'profile_picture',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'profile_picture']

    def get_name(self, obj):
        return obj.full_name or obj.username

    def get_profile_picture(self, obj):
        try:
            if hasattr(obj, 'profile') and obj.profile.profile_picture:
                url = obj.profile.profile_picture.url
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(url)
                return url
        except Exception:
            pass
        return None


class LoginSerializer(serializers.Serializer):
    """
    Validates credentials (email or username + password) and authenticates.
    """
    identifier = serializers.CharField(
        required=True,
        error_messages={'blank': 'Please enter your email or Student ID.'}
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        error_messages={'blank': 'Please enter your password.'}
    )

    def validate(self, attrs):
        identifier = attrs.get('identifier', '').strip()
        password = attrs.get('password', '')

        if not identifier or not password:
            raise serializers.ValidationError('Invalid email or password.')

        user = authenticate(username=identifier, password=password)
        if not user:
            raise serializers.ValidationError('Invalid email or password.')

        if not user.is_active:
            raise serializers.ValidationError('This user account is inactive. Please contact your administrator.')

        attrs['user'] = user
        return attrs


from .models import User, ApprovedStudent


class RegisterSerializer(serializers.ModelSerializer):
    """
    Registration serializer enforcing approved students, password validation,
    and automatic STUDENT role assignment.
    """
    full_name = serializers.CharField(
        required=True,
        error_messages={'blank': 'Please enter your full name.'}
    )
    email = serializers.EmailField(
        required=True,
        validators=[],  # Custom validated in validate_email for exact error messaging
        error_messages={'blank': 'Please enter your college email.'}
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        error_messages={'blank': 'Please enter a password.'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        error_messages={'blank': 'Please confirm your password.'}
    )
    username = serializers.CharField(
        required=False,
        allow_blank=True
    )

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'full_name',
            'role',
            'password',
            'password_confirm'
        ]
        read_only_fields = ['id', 'role']

    def to_internal_value(self, data):
        if isinstance(data, dict):
            mutable_data = data.copy()
            if 'name' in mutable_data and 'full_name' not in mutable_data:
                mutable_data['full_name'] = mutable_data['name']
            data = mutable_data
        return super().to_internal_value(data)

    def validate_email(self, value):
        # CHECK 1: Valid email format is handled by EmailField
        email = value.strip().lower()

        # CHECK 2: Is the email present in the APPROVED STUDENT list?
        approved = ApprovedStudent.objects.filter(email__iexact=email).first()
        if not approved:
            raise serializers.ValidationError(
                "Registration is allowed only for approved MMCOE college email addresses."
            )

        # CHECK 3: Has this approved student already registered?
        if approved.is_registered:
            raise serializers.ValidationError(
                "An account with this email already exists. Please log in."
            )

        # CHECK 4: Does an actual Django User already exist with this email?
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "An account with this email already exists. Please log in."
            )

        return email

    def validate(self, attrs):
        # CHECK 5: Password validity is handled by validate_password validator

        # CHECK 6: Does Password match Confirm Password?
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.',
                'detail': 'Passwords do not match.'
            })

        # Name normalization from approved record if appropriate
        email = attrs.get('email', '').strip().lower()
        approved = ApprovedStudent.objects.filter(email__iexact=email).first()
        if approved:
            entered_name = attrs.get('full_name', '').strip()
            if not entered_name:
                attrs['full_name'] = approved.name
            elif entered_name.lower() == approved.name.split()[0].lower() and len(approved.name.split()) > 1:
                attrs['full_name'] = approved.name

        # Auto-generate username from email if not provided
        if not attrs.get('username'):
            base_username = email.split('@')[0] if '@' in email else 'student'
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            attrs['username'] = username

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        # Public registration must strictly enforce STUDENT role
        validated_data['role'] = User.Role.STUDENT

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        # Mark approved student registration record as Registered
        email = validated_data.get('email', '').strip().lower()
        ApprovedStudent.objects.filter(email__iexact=email).update(is_registered=True)

        return user
