from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authenticate against settings.AUTH_USER_MODEL using either email or username/student ID.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
        if username is None or password is None:
            return None

        identifier = username.strip()
        user = User.objects.filter(
            Q(email__iexact=identifier) | Q(username__iexact=identifier)
        ).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
