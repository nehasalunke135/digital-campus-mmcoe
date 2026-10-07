from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.authtoken.models import Token
from django.contrib.auth import login as django_login, logout as django_logout

from .models import User
from .serializers import UserSerializer, LoginSerializer, RegisterSerializer
from .permissions import IsStudent, IsAdminUserRole


class LoginView(APIView):
    """
    Common login endpoint for all users (STUDENT and ADMIN).
    Validates credentials and returns an auth token along with verified user data.
    """
    permission_classes = [AllowAny]
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            errors = serializer.errors
            detail = 'Invalid email or password.'
            return Response({
                **errors,
                'detail': detail,
                'error': detail,
                'message': detail,
                'non_field_errors': [detail]
            }, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        # Optional session support for web sessions
        if hasattr(request, 'session'):
            django_login(request, user)

        user_data = UserSerializer(user, context={'request': request}).data
        return Response({
            'token': token.key,
            'user': user_data,
            'message': 'Login successful.'
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Common logout endpoint. Invalidates the auth token and clears session.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Delete token if exists
        try:
            if hasattr(request.user, 'auth_token'):
                request.user.auth_token.delete()
        except Exception:
            pass

        if hasattr(request, 'session'):
            django_logout(request)

        return Response({
            'message': 'Successfully logged out.'
        }, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    """
    Returns the currently authenticated user's profile and verified role,
    and supports updating user fields (names, avatar/profile picture).
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        full_name = data.get('full_name')

        updated = False
        if first_name is not None:
            user.first_name = first_name.strip()
            updated = True
        if last_name is not None:
            user.last_name = last_name.strip()
            updated = True
        if full_name is not None:
            user.full_name = full_name.strip()
            updated = True
        elif first_name is not None or last_name is not None:
            combined = f"{user.first_name} {user.last_name}".strip()
            if combined:
                user.full_name = combined
                updated = True

        if updated:
            user.save()

        # Handle profile picture upload or removal
        remove_picture = data.get('remove_profile_picture')
        if remove_picture in [True, 'true', '1', 1]:
            from posts.models import UserProfile
            if hasattr(user, 'profile') and user.profile.profile_picture:
                try:
                    user.profile.profile_picture.delete(save=False)
                except Exception:
                    pass
                user.profile.profile_picture = None
                user.profile.save()
        elif 'profile_picture' in request.FILES:
            from posts.models import UserProfile
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()

        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        user = request.user
        if hasattr(user, 'profile') and user.profile.profile_picture:
            try:
                user.profile.profile_picture.delete(save=False)
            except Exception:
                pass
            user.profile.profile_picture = None
            user.profile.save()

        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)


class RegisterView(APIView):
    """
    Registration endpoint for creating new student users.
    Enforces approved email addresses and strictly assigns STUDENT role.
    """
    permission_classes = [AllowAny]
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            errors = serializer.errors
            detail = 'Registration validation failed.'
            # Check priority fields for clean exact error message
            for field in ['password_confirm', 'email', 'non_field_errors', 'password', 'full_name', 'detail']:
                if field in errors:
                    v = errors[field]
                    if isinstance(v, list) and len(v) > 0:
                        detail = str(v[0])
                    elif isinstance(v, str):
                        detail = v
                    break
            return Response({
                **errors,
                'detail': detail,
                'error': detail,
                'message': detail
            }, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user).data
        return Response({
            'token': token.key,
            'user': user_data,
            'message': 'Registration successful. Please log in.'
        }, status=status.HTTP_201_CREATED)


class StudentOnlyTestView(APIView):
    """
    Protected sample endpoint verifying STUDENT role access.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        return Response({
            'message': f"Access granted to Student area. Welcome {request.user.full_name or request.user.username}!",
            'role': request.user.role
        })


class AdminOnlyTestView(APIView):
    """
    Protected sample endpoint verifying ADMIN role access.
    """
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def get(self, request):
        return Response({
            'message': f"Access granted to Admin area. Welcome {request.user.full_name or request.user.username}!",
            'role': request.user.role
        })
