from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from posts.models import Post
from .models import Comment
from .permissions import IsOwnerOrReadOnly
from .serializers import CommentSerializer


class CommentPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostCommentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/posts/<post_id>/comments/ - Publicly list all comments on a post (paginated).
    POST /api/v1/posts/<post_id>/comments/ - Add a comment to the post (authenticated users only).
    """
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = CommentPagination

    def get_queryset(self):
        # Verify the post exists; returns 404 if not found
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return Comment.objects.filter(post=post).select_related('author')

    def perform_create(self, serializer):
        # Fetch post from URL route to guarantee no payload spoofing
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        serializer.save(author=self.request.user, post=post)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/comments/<id>/ - Public read of comment detail.
    PUT    /api/v1/comments/<id>/ - Update comment (author only).
    PATCH  /api/v1/comments/<id>/ - Partial update comment (author only).
    DELETE /api/v1/comments/<id>/ - Delete comment (author only).
    """
    queryset = Comment.objects.select_related('author', 'post').all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]
