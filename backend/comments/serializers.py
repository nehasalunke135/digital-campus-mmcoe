from rest_framework import serializers
from posts.serializers import AuthorPublicSerializer
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comments attached to posts.
    Nests public author representation to prevent leaking sensitive fields.
    Post is read-only and bound to the URL parameter to prevent payload tampering.
    """
    author = AuthorPublicSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'post',
            'author',
            'content',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'post', 'author', 'created_at', 'updated_at']

    def validate_content(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Comment content cannot be empty or blank.")
        return cleaned
