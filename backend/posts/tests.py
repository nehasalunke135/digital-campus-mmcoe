import io
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Post, PostLike



User = get_user_model()


class PostAPITests(APITestCase):
    """
    Test suite for posts CRUD, permission enforcement, author isolation, and pagination.
    """

    def setUp(self):
        self.list_create_url = reverse('posts:post-list-create')

        self.author = User.objects.create_user(
            username='postauthor',
            email='author@college.edu',
            password='AuthorPassword123!'
        )
        self.other_user = User.objects.create_user(
            username='otherstudent',
            email='other@college.edu',
            password='OtherPassword123!'
        )

        self.post = Post.objects.create(
            author=self.author,
            title='Campus Orientation',
            content='Welcome to the new semester!'
        )
        self.detail_url = reverse('posts:post-detail', kwargs={'pk': self.post.pk})

    def test_public_can_list_posts(self):
        """Ensure unauthenticated users can view the list of posts."""
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should be paginated
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Campus Orientation')
        self.assertEqual(response.data['results'][0]['author']['username'], 'postauthor')

    def test_public_can_retrieve_single_post(self):
        """Ensure unauthenticated users can retrieve a single post detail."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Campus Orientation')
        self.assertEqual(response.data['author']['id'], self.author.id)
        self.assertEqual(response.data['author']['username'], 'postauthor')

    def test_unauthenticated_cannot_create_post(self):
        """Ensure unauthenticated users get 401 when trying to create a post."""
        data = {'title': 'Hackathon', 'content': 'Join us this weekend!'}
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_create_post(self):
        """Ensure authenticated user can create a post with author set server-side."""
        self.client.force_authenticate(user=self.author)
        data = {
            'title': 'Library Hours',
            'content': 'Open 24/7 during finals week.',
            'author': self.other_user.id  # Attempt to spoof author
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Library Hours')
        # Ensure server forced author to request.user, ignoring payload spoofing
        self.assertEqual(response.data['author']['username'], 'postauthor')
        self.assertEqual(response.data['author']['id'], self.author.id)

    def test_owner_can_update_post(self):
        """Ensure post owner can update post via PUT or PATCH."""
        self.client.force_authenticate(user=self.author)
        data = {'title': 'Updated Title', 'content': 'Updated content.'}
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

        patch_data = {'title': 'Partially Updated Title'}
        patch_response = self.client.patch(self.detail_url, patch_data, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['title'], 'Partially Updated Title')

    def test_non_owner_cannot_update_post(self):
        """Ensure non-owner receives 403 Forbidden when trying to update another user's post."""
        self.client.force_authenticate(user=self.other_user)
        data = {'title': 'Malicious Edit', 'content': 'Hacked content.'}
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_post(self):
        """Ensure post author can delete their post."""
        self.client.force_authenticate(user=self.author)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_non_owner_cannot_delete_post(self):
        """Ensure non-owner receives 403 Forbidden when attempting to delete another's post."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_posts_pagination(self):
        """Ensure post listing supports pagination and ordering."""
        # Create 15 additional posts
        posts = [
            Post(author=self.author, title=f"Post #{i}", content=f"Body {i}")
            for i in range(15)
        ]
        Post.objects.bulk_create(posts)

        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 16)
        self.assertEqual(len(response.data['results']), 10)  # Default page size = 10
        self.assertIsNotNone(response.data['next'])

    def test_authenticated_can_create_post_with_image(self):
        """Ensure authenticated user can create a post with an uploaded image via multipart/form-data."""
        self.client.force_authenticate(user=self.author)

        # Create in-memory test image
        img_file = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(img_file, 'JPEG')
        img_file.seek(0)

        uploaded_image = SimpleUploadedFile(
            name='test_post_image.jpg',
            content=img_file.read(),
            content_type='image/jpeg'
        )

        data = {
            'title': 'Campus Event Photo',
            'content': 'Check out this photo from the event!',
            'image': uploaded_image
        }

        response = self.client.post(self.list_create_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Campus Event Photo')
        self.assertIsNotNone(response.data['image'])
        self.assertIn('/media/post_images/', response.data['image'])

        # Verify Post object created in database has image populated
        created_post = Post.objects.get(pk=response.data['id'])
        self.assertTrue(bool(created_post.image))
        self.assertTrue(created_post.image.name.startswith('post_images/'))

    def test_unauthenticated_cannot_toggle_like(self):
        """Ensure unauthenticated users get 401 when trying to toggle like."""
        like_url = reverse('posts:post-like-toggle', kwargs={'pk': self.post.pk})
        response = self.client.post(like_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_post_returns_404_on_like(self):
        """Ensure toggling like on a non-existent post returns 404 Not Found."""
        self.client.force_authenticate(user=self.author)
        like_url = reverse('posts:post-like-toggle', kwargs={'pk': 999999})
        response = self.client.post(like_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_can_like_and_unlike_post(self):
        """Ensure toggling like works: first call likes, second call unlikes."""
        like_url = reverse('posts:post-like-toggle', kwargs={'pk': self.post.pk})
        self.client.force_authenticate(user=self.author)

        # 1. Like the post
        res1 = self.client.post(like_url)
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res1.data, {'liked': True, 'like_count': 1})
        self.assertEqual(PostLike.objects.filter(post=self.post, user=self.author).count(), 1)

        # Verify serializer reflects is_liked=True and like_count=1
        detail_res = self.client.get(self.detail_url)
        self.assertEqual(detail_res.data['like_count'], 1)
        self.assertEqual(detail_res.data['is_liked'], True)

        # 2. Toggle again (unlike)
        res2 = self.client.post(like_url)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.data, {'liked': False, 'like_count': 0})
        self.assertEqual(PostLike.objects.filter(post=self.post, user=self.author).count(), 0)

        # Verify serializer reflects is_liked=False and like_count=0
        detail_res2 = self.client.get(self.detail_url)
        self.assertEqual(detail_res2.data['like_count'], 0)
        self.assertEqual(detail_res2.data['is_liked'], False)

    def test_multiple_users_can_independently_like_same_post(self):
        """Ensure different users can independently like the same post."""
        like_url = reverse('posts:post-like-toggle', kwargs={'pk': self.post.pk})

        # Author likes post
        self.client.force_authenticate(user=self.author)
        res_author = self.client.post(like_url)
        self.assertEqual(res_author.data, {'liked': True, 'like_count': 1})

        # Other user likes post
        self.client.force_authenticate(user=self.other_user)
        res_other = self.client.post(like_url)
        self.assertEqual(res_other.data, {'liked': True, 'like_count': 2})
        self.assertEqual(PostLike.objects.filter(post=self.post).count(), 2)

        # Serializer for other_user shows is_liked=True, like_count=2
        detail_other = self.client.get(self.detail_url)
        self.assertEqual(detail_other.data['like_count'], 2)
        self.assertEqual(detail_other.data['is_liked'], True)

        # Unauthenticated request shows like_count=2, is_liked=False
        self.client.logout()
        detail_anon = self.client.get(self.detail_url)
        self.assertEqual(detail_anon.data['like_count'], 2)
        self.assertEqual(detail_anon.data['is_liked'], False)

    def test_duplicate_likes_prevented_by_unique_constraint(self):
        """Ensure duplicate PostLike rows cannot be created for same (post, user)."""
        PostLike.objects.create(post=self.post, user=self.author)

        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            PostLike.objects.create(post=self.post, user=self.author)


