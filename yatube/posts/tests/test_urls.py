from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Post, Group, Follow

User = get_user_model()


class YatubeURLTests(TestCase):
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
            text='Тестовый пост',
            author=cls.user,
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.post.author,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_public_urls_exists_at_desired_location(self):
        """Страницы из списка доступны любому пользователю."""
        urls_list = [
            '/',
            f'/group/{self.group.slug}/',
            f'/posts/{self.post.id}/'
        ]
        for url in urls_list:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_at_desired_location(self):
        """Страницы из списка доступны авторизованным пользователям."""
        urls_list = [
            '/',
            f'/group/{self.group.slug}/',
            f'/posts/{self.post.id}/',
            '/create/',
        ]
        for url in urls_list:
            response = self.authorized_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_anonymous_on_admin_login(self):
        """Страница create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_urls_redirect_profile_follow(self):
        """
        Страница profile_follow перенаправит авторизованного
        пользователя на страницу автора.
        """
        response = self.authorized_client.get(
            f'/profile/{self.user.username}/follow/',
            follow=True
        )
        self.assertRedirects(
            response, f'/profile/{self.user.username}/'
        )

    def test_urls_redirect_add_comment(self):
        """
        Страница add_comment перенаправит авторизованного
        пользователя на страницу поста.
        """
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/comment/',
            follow=True
        )
        self.assertRedirects(
            response, f'/posts/{self.post.id}/'
        )

    def test_404_error(self):
        """Ошибка 404 для несуществующей страницы."""
        url = '/unexisting_page/'
        response = self.guest_client.get(url, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
