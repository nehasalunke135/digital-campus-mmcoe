from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Comment model.
    """
    list_display = ('id', 'post', 'author', 'content_snippet', 'created_at', 'updated_at')
    search_fields = ('content', 'author__username', 'author__email', 'post__title')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    def content_snippet(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_snippet.short_description = 'Content'
