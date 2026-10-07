from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User


class AuthenticationTests(APITestCase):
    def setUp(self):
        # Create Student A
        self.student_a = User.objects.create_user(
            email='student.a@gmail.com',
            username='student_a',
            password='Studenta@123',
            full_name='Student A',
            role=User.Role.STUDENT
        )

        # Create Student B
        self.student_b = User.objects.create_user(
            email='student.b@gmail.com',
            username='student_b',
            password='Studentb@123',
            full_name='Student B',
            role=User.Role.STUDENT
        )

        # Create Admin
        self.admin = User.objects.create_user(
            email='admin@gmail.com',
            username='admin',
            password='Admin@123',
            full_name='Admin',
            role=User.Role.ADMIN
        )

        self.login_url = reverse('auth-login')
        self.logout_url = reverse('auth-logout')
        self.me_url = reverse('auth-me')
        self.register_url = reverse('auth-register')
        self.student_only_url = reverse('auth-student-only')
        self.admin_only_url = reverse('auth-admin-only')

    def test_student_a_login_with_email(self):
        """Student A can login using email address"""
        response = self.client.post(self.login_url, {
            'identifier': 'student.a@gmail.com',
            'password': 'Studenta@123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['role'], 'STUDENT')
        self.assertEqual(response.data['user']['email'], 'student.a@gmail.com')
        self.assertEqual(response.data['user']['full_name'], 'Student A')

    def test_student_a_login_with_username(self):
        """Student A can login using username"""
        response = self.client.post(self.login_url, {
            'identifier': 'student_a',
            'password': 'Studenta@123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['role'], 'STUDENT')
        self.assertEqual(response.data['user']['full_name'], 'Student A')

    def test_student_b_login_with_email(self):
        """Student B can login using email address"""
        response = self.client.post(self.login_url, {
            'identifier': 'student.b@gmail.com',
            'password': 'Studentb@123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['role'], 'STUDENT')
        self.assertEqual(response.data['user']['email'], 'student.b@gmail.com')
        self.assertEqual(response.data['user']['full_name'], 'Student B')

    def test_admin_login(self):
        """Admin uses the EXACT SAME login endpoint and User model"""
        response = self.client.post(self.login_url, {
            'identifier': 'admin@gmail.com',
            'password': 'Admin@123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['role'], 'ADMIN')
        self.assertEqual(response.data['user']['email'], 'admin@gmail.com')
        self.assertEqual(response.data['user']['full_name'], 'Admin')

    def test_invalid_password(self):
        """Invalid credentials are rejected"""
        response = self.client.post(self.login_url, {
            'identifier': 'student.a@gmail.com',
            'password': 'WrongPassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_current_user_me(self):
        """Current authenticated user is returned with role and full_name"""
        login_resp = self.client.post(self.login_url, {
            'identifier': 'student.a@gmail.com',
            'password': 'Studenta@123'
        })
        token = login_resp.data['token']

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        me_resp = self.client.get(self.me_url)
        self.assertEqual(me_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(me_resp.data['email'], 'student.a@gmail.com')
        self.assertEqual(me_resp.data['full_name'], 'Student A')
        self.assertEqual(me_resp.data['role'], 'STUDENT')

    def test_logout_invalidates_token(self):
        """Logout removes auth token"""
        login_resp = self.client.post(self.login_url, {
            'identifier': 'student.a@gmail.com',
            'password': 'Studenta@123'
        })
        token = login_resp.data['token']

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        logout_resp = self.client.post(self.logout_url)
        self.assertEqual(logout_resp.status_code, status.HTTP_200_OK)

        # Subsequent request with old token is rejected
        me_resp = self.client.get(self.me_url)
        self.assertEqual(me_resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_role_based_permissions(self):
        """Backend authorization enforces roles"""
        # 1. Student accessing student-only: OK
        self.client.force_authenticate(user=self.student_a)
        resp = self.client.get(self.student_only_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # 2. Student accessing admin-only: FORBIDDEN
        resp = self.client.get(self.admin_only_url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Admin accessing admin-only: OK
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.admin_only_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # 4. Admin accessing student-only: FORBIDDEN
        resp = self.client.get(self.student_only_url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_with_active_session_no_csrf_failure(self):
        """
        Verify that login does not fail with 'CSRF Failed: CSRF token missing.'
        even when browser session cookies or enforce_csrf_checks are enabled.
        """
        csrf_client = self.client_class(enforce_csrf_checks=True)
        home_resp = csrf_client.get('/')
        self.assertEqual(home_resp.status_code, status.HTTP_200_OK)

        resp = csrf_client.post(self.login_url, {
            'identifier': 'student.a@gmail.com',
            'password': 'Studenta@123'
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('token', resp.data)

