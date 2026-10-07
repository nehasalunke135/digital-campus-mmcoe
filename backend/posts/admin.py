from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin configuration for Post model.
    """
    list_display = ('id', 'title', 'author', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'author__username', 'author__email')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
