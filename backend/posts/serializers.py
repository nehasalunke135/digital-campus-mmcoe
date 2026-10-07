from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Post, PostLike

User = get_user_model()


class AuthorPublicSerializer(serializers.ModelSerializer):
    """
    Compact user representation embedded in posts and comments.
    """
    name = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'name', 'role', 'profile_picture']
        read_only_fields = ['id', 'username', 'email', 'full_name', 'name', 'role', 'profile_picture']

    def get_name(self, obj):
        return getattr(obj, 'full_name', '') or obj.username

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


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for campus posts.
    Includes post image URL, real database like count, and is_liked status for authenticated user.
    """
    author = AuthorPublicSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'title',
            'content',
            'image',
            'like_count',
            'is_liked',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def validate_title(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Title cannot be empty or blank.")
        if len(cleaned) > 200:
            raise serializers.ValidationError("Title cannot exceed 200 characters.")
        return cleaned

    def validate_content(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Content cannot be empty or blank.")
        return cleaned
