from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ApprovedStudent


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'full_name', 'role', 'is_staff', 'is_active', 'created_at')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'full_name')}),
        ('Role & Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'full_name', 'role', 'password', 'password_confirm'),
        }),
    )
    search_fields = ('email', 'username', 'full_name')
    ordering = ('-created_at',)


@admin.register(ApprovedStudent)
class ApprovedStudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_registered', 'created_at', 'updated_at')
    list_filter = ('is_registered',)
    search_fields = ('name', 'email')
    ordering = ('name',)
