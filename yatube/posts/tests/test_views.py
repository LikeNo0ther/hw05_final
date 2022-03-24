from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group, Comment, Follow


User = get_user_model()


class YatubeViewsTests(TestCase):
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
            group=YatubeViewsTests.group,
            text='Тестовый пост',
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': 'TestUser'}): (
                'posts/profile.html'
            ),
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{self.post.id}'}
            ): ('posts/create_post.html'),
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def post_attributes(self, post_obj):
        """Проверка атрибутов поста."""
        post_text_0 = post_obj.text
        post_author_0 = post_obj.author
        post_group_0 = post_obj.group.title
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_group_0, self.group.title)

    def test_index_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.post_attributes(first_object)

    def test_group_list_shows_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[self.group.slug])
        )
        first_object = response.context['page_obj'][0]
        self.post_attributes(first_object)

    def test_profile_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', args=[self.post.author])
        )
        first_object = response.context['page_obj'][0]
        self.post_attributes(first_object)

    def test_post_edit_shows_correct_context(self):
        """Шаблон редактирования поста сформирован с правильным контекстом."""
        post_id = YatubeViewsTests.post.id
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post_id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_shows_correct_context(self):
        """Шаблон создания поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_add_comment(self):
        """Проверка добавления комментария зарегистрированным пользователем."""
        post_id = YatubeViewsTests.post.id
        form_data = {'text': 'очень занимательно'}
        self.authorized_client.post(
            reverse('posts:add_comment', args=[post_id]),
            data=form_data,
            follow=True,
        )
        comment = (Comment.objects.filter(author=self.user).last())
        self.assertEqual(form_data['text'], comment.text)
        self.assertEqual(str(comment.author), f'{self.user}')
        self.assertEqual(post_id, comment.post.id)

    def test_follow_unfollow(self):
        """
        Проверка подписки зарегистрированным пользователем
        на автора и удаления его из подписок.
        """
        counter_before = Follow.objects.all().filter(
            author_id=self.post.author.id).count()
        self.authorized_client.get(reverse(
            'posts:profile_follow', args=[self.post.author]))
        counter_after_sub = Follow.objects.all().filter(
            author_id=self.post.author.id).count()
        self.assertEqual(counter_after_sub, counter_before + 1)
        self.authorized_client.get(reverse(
            'posts:profile_unfollow', args=[self.post.author]))
        counter_after_unsub = Follow.objects.all().filter(
            author_id=self.post.author.id).count()
        self.assertEqual(counter_after_unsub, counter_before)

    def test_profile_follow_works_correct(self):
        """Проверка корректности появления статей избранных авторов."""
        response_before_sub = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.authorized_client.get(
            reverse('posts:profile_follow', args=[self.post.author]))
        response_after_sub = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertNotEqual(
            response_before_sub.context['page_obj'],
            response_after_sub.context['page_obj']
        )


class PaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Pag')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(13):
            cls.post = Post.objects.create(
                group=PaginatorViewsTests.group,
                text='Тестовый текст',
                author=User.objects.get(username='Pag'),
            )

    def test_first_page_index_contains_ten_records(self):
        """Тест корректности работы index пагинатора 1/2."""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_index_contains_three_records(self):
        """Тест корректности работы index пагинатора 2/2."""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_group_list_contains_ten_records(self):
        """Тест корректности работы group_list пагинатора 1/2."""
        response = self.client.get(f'/group/{self.group.slug}/')
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_group_list_contains_three_records(self):
        """Тест корректности работы group_list пагинатора 2/2."""
        response = self.client.get(f'/group/{self.group.slug}/' + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_profile_contains_ten_records(self):
        """Тест корректности работы profile пагинатора 1/2."""
        response = self.client.get(f'/profile/{self.user.username}/')
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_profile_contains_three_records(self):
        """Тест корректности работы profile пагинатора 2/2."""
        response = self.client.get(
            f'/profile/{self.user.username}/' + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)
