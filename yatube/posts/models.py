from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        verbose_name='Сообщение',
        help_text='Введите сообщение'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата',
        help_text='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Автор публикации'
    )
    group = models.ForeignKey(
        'Group', blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name_plural = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
        help_text='Укажите заголовок'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='url',
        help_text='Укажите url'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Укажите описание'
    )

    class Meta:
        verbose_name_plural = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Укажите свой комментарий'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время',
        help_text='Дата и время публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
        help_text='Автор публикации'
    )
    post = models.ForeignKey(
        'Post', blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='comments',
        verbose_name='Пост',
        help_text='Пост'
    )
    moderation = models.BooleanField('Модерация', default=False)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name_plural = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author}'


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Автор публикации'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )

    class Meta:
        models.UniqueConstraint(
            fields=['author', 'user'],
            name='unique_following'
        )
        verbose_name_plural = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
