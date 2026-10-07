from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    CurrentUserView,
    RegisterView,
    StudentOnlyTestView,
    AdminOnlyTestView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('me/', CurrentUserView.as_view(), name='auth-me'),
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('student-only/', StudentOnlyTestView.as_view(), name='auth-student-only'),
    path('admin-only/', AdminOnlyTestView.as_view(), name='auth-admin-only'),
]
