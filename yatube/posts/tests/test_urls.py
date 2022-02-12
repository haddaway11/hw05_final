from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from http import HTTPStatus
from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст поста',
        )
        cls.urls = [
            reverse('posts:index'),
            reverse('posts:group_posts',
                    kwargs={'slug':
                            PostURLTests.group.slug}),
            reverse('posts:profile',
                    kwargs={'username':
                            PostURLTests.user.username}),
            reverse('posts:post_detail',
                    kwargs={'post_id':
                            PostURLTests.post.id}),
        ]
        cls.templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug':
                            PostURLTests.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username':
                            PostURLTests.user.username}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id':
                            PostURLTests.post.id}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id':
                            PostURLTests.post.id}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_url_exists_at_desired_location(self):
        """Страницы доступны любому и авторизованным пользователям."""
        for request_client in (self.guest_client, self.authorized_client):
            for url in self.urls:
                with self.subTest(url=url, request_client=request_client):
                    response = request_client.get(url, follow=True)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
        urls = [
            reverse('posts:post_edit',
                    kwargs={'post_id':
                            PostURLTests.post.id}),
            reverse('posts:post_create'),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_redirect_anonymous(self):
        """Страница /post_id/edit перенаправляет анонимного пользователя."""
        response = self.guest_client.get(reverse('posts:post_edit',
                                                 kwargs={'post_id':
                                                         PostURLTests.
                                                         post.id}))
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_post_create_url_redirect_anonymous(self):
        """Страница /posts/create/ перенаправляет анонимного пользователя. """
        response = self.guest_client.get(reverse('posts:post_create'),
                                         follow=True)
        self.assertRedirects(response, ('/auth/login/?next=/create/'))

    def test_unexisting_page(self):
        """Запрос к страница unixisting_page вернет ошибку 404"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_error_page(self):
        """Запрос к страница nonexist-page вернет шаблон 404.html"""
        response = self.guest_client.get('/nonexist_page/')
        self.assertTemplateUsed(response, 'core/404.html')
        response = self.authorized_client.get('/nonexist_page/')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in self.templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
