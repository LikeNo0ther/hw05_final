from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User, Comment
from posts.forms import PostForm


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_form(self):
        """При отправке формы создается новая запсь в БД."""
        counter = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile',
                args=[self.user.username]
            )
        )
        self.assertEqual(Post.objects.count(), counter + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                group=PostFormTest.group,
            ).exists()
        )

    def test_edit_post_form(self):
        """При редактировании поста происходит изменение в БД."""
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.get(username='author'),
            group=PostFormTest.group,
        )
        self.form = PostForm()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client.get(
            reverse('posts:post_edit', args=(1,))
        )
        form_data = {
            'text': 'Забыл уточнить',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', args=(1,)),
            data=form_data, follow=True
        )
        self.assertTrue(Post.objects.filter(
            text='Забыл уточнить',
            group=PostFormTest.group).exists()
        )


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_comment_form(self):
        """При отправке формы создается новая запсь в БД."""
        counter = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', args=[CommentFormTest.post.id]),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), counter + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый комментарий',
                post=CommentFormTest.post.id,
            ).exists()
        )
