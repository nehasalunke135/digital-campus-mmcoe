from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from .models import Post, PostLike
from .permissions import IsOwnerOrReadOnly
from .serializers import PostSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/posts/       - Publicly lists posts, paginated, newest first.
    POST /api/v1/posts/       - Creates a new post (authenticated users only).
    """
    queryset = Post.objects.select_related('author').all()
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        # Author is strictly determined server-side from request.user
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/posts/<id>/ - Public read of post detail.
    PUT    /api/v1/posts/<id>/ - Full update (author only).
    PATCH  /api/v1/posts/<id>/ - Partial update (author only).
    DELETE /api/v1/posts/<id>/ - Delete post (author only).
    """
    queryset = Post.objects.select_related('author').all()
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class PostLikeToggleView(APIView):
    """
    POST /api/v1/posts/<int:pk>/like/
    Toggles post like status for authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        like, created = PostLike.objects.get_or_create(post=post, user=request.user)

        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        like_count = post.likes.count()
        return Response({
            'liked': liked,
            'like_count': like_count
        }, status=status.HTTP_200_OK)


