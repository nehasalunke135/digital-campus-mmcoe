from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom user manager where email or username can be used for authentication.
    """
    def create_user(self, email, username=None, password=None, full_name='', role='STUDENT', **extra_fields):
        if not email:
            raise ValueError('The Email field is required')
        email = self.normalize_email(email)
        if not username:
            username = email.split('@')[0]
        user = self.model(
            email=email,
            username=username,
            full_name=full_name,
            role=role,
            **extra_fields
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, full_name='Administrator', **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(
            email=email,
            username=username,
            password=password,
            full_name=full_name,
            **extra_fields
        )


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        ADMIN = 'ADMIN', 'Admin'

    email = models.EmailField('email address', unique=True)
    username = models.CharField('username / student ID', max_length=150, unique=True)
    full_name = models.CharField('full name', max_length=255, blank=True)
    role = models.CharField(
        'role',
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name or self.username} ({self.role}) - {self.email}"

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_staff or self.is_superuser


class ApprovedStudent(models.Model):
    """
    Approved student registration record.
    Represents registration eligibility, NOT an active Django User account.
    A Django User account is created ONLY upon successful registration.
    """
    name = models.CharField('student name', max_length=255)
    email = models.EmailField('approved college email', unique=True)
    is_registered = models.BooleanField('registration status', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'approved student'
        verbose_name_plural = 'approved students'
        ordering = ['name']

    def __str__(self):
        status = "Registered" if self.is_registered else "Not Registered"
        return f"{self.name} ({self.email}) - {status}"
