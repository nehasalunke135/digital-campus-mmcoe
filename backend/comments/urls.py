from django.urls import path
from .views import PostCommentListCreateView, CommentDetailView

app_name = 'comments'

urlpatterns = [
    path('posts/<int:post_id>/comments/', PostCommentListCreateView.as_view(), name='post-comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
]
