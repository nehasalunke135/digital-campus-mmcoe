from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from posts.models import Post
from .models import Comment

User = get_user_model()


class CommentAPITests(APITestCase):
    """
    Test suite for comments CRUD, post binding integrity, permissions, and pagination.
    """

    def setUp(self):
        self.comment_author = User.objects.create_user(
            username='commenter',
            email='commenter@college.edu',
            password='Password123!'
        )
        self.other_user = User.objects.create_user(
            username='otherstudent',
            email='other@college.edu',
            password='Password123!'
        )

        self.post = Post.objects.create(
            author=self.comment_author,
            title='College Festival Announcement',
            content='Spring fest starts next Monday.'
        )
        self.other_post = Post.objects.create(
            author=self.other_user,
            title='Lost and Found',
            content='Found a calculator in Room 204.'
        )

        self.comment = Comment.objects.create(
            post=self.post,
            author=self.comment_author,
            content='Looking forward to the fest!'
        )

        self.post_comments_url = reverse(
            'comments:post-comment-list-create',
            kwargs={'post_id': self.post.id}
        )
        self.comment_detail_url = reverse(
            'comments:comment-detail',
            kwargs={'pk': self.comment.pk}
        )

    def test_public_can_list_comments_for_post(self):
        """Ensure unauthenticated users can list comments for a post."""
        response = self.client.get(self.post_comments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], 'Looking forward to the fest!')
        self.assertEqual(response.data['results'][0]['author']['username'], 'commenter')

    def test_list_comments_for_nonexistent_post_returns_404(self):
        """Ensure requesting comments for a post that doesn't exist returns 404."""
        nonexistent_url = reverse('comments:post-comment-list-create', kwargs={'post_id': 99999})
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_cannot_create_comment(self):
        """Ensure unauthenticated users receive 401 when attempting to comment."""
        data = {'content': 'Is attendance mandatory?'}
        response = self.client.post(self.post_comments_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_create_comment(self):
        """Ensure authenticated user can post a comment tied to the route post."""
        self.client.force_authenticate(user=self.comment_author)
        data = {
            'content': 'Can non-students attend?',
            'post': self.other_post.id  # Attempt to spoof post id
        }
        response = self.client.post(self.post_comments_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Can non-students attend?')
        # Verify the comment is strictly attached to the URL post, not payload spoof
        self.assertEqual(response.data['post'], self.post.id)
        self.assertEqual(response.data['author']['username'], 'commenter')

    def test_create_comment_on_nonexistent_post_returns_404(self):
        """Ensure attempting to comment on a non-existent post returns 404."""
        self.client.force_authenticate(user=self.comment_author)
        nonexistent_url = reverse('comments:post-comment-list-create', kwargs={'post_id': 99999})
        response = self.client.post(nonexistent_url, {'content': 'Hello'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_update_comment(self):
        """Ensure comment owner can update their comment."""
        self.client.force_authenticate(user=self.comment_author)
        data = {'content': 'Edited comment content.'}
        response = self.client.put(self.comment_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Edited comment content.')

    def test_non_owner_cannot_update_comment(self):
        """Ensure non-owner receives 403 when attempting to edit another's comment."""
        self.client.force_authenticate(user=self.other_user)
        data = {'content': 'Unauthorized edit'}
        response = self.client.put(self.comment_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_comment(self):
        """Ensure comment owner can delete their comment."""
        self.client.force_authenticate(user=self.comment_author)
        response = self.client.delete(self.comment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_non_owner_cannot_delete_comment(self):
        """Ensure non-owner receives 403 when trying to delete another user's comment."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.comment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_comments_pagination(self):
        """Ensure per-post comments list is paginated."""
        # Create 12 more comments on this post
        comments = [
            Comment(post=self.post, author=self.comment_author, content=f"Comment #{i}")
            for i in range(12)
        ]
        Comment.objects.bulk_create(comments)

        response = self.client.get(self.post_comments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 13)
        self.assertEqual(len(response.data['results']), 10)  # Default page size
        self.assertIsNotNone(response.data['next'])
