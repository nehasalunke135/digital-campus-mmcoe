from django.urls import path
from .views import PostListCreateView, PostDetailView, PostLikeToggleView

app_name = 'posts'

urlpatterns = [
    path('', PostListCreateView.as_view(), name='post-list-create'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('<int:pk>/like/', PostLikeToggleView.as_view(), name='post-like-toggle'),
]

