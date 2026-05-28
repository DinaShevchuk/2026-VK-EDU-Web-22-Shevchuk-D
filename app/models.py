from django.db import models
from django.core.validators import FileExtensionValidator
import os
import uuid
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class QuestionManager(models.Manager):
    """Менеджер для типовых выборок вопросов"""

    def get_new(self):
        """Новые вопросы (сначала свежие)"""
        return self.order_by('-created_at')

    def get_best(self):
        """Лучшие вопросы (по рейтингу)"""
        return self.order_by('-rating')

    def get_by_tag(self, tag_name):
        """Вопросы по тегу"""
        return self.filter(tags__name=tag_name)


class Profile(models.Model):
    """Профиль пользователя (расширение встроенного User)"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="profile"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Аватар"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата регистрации"
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль: {self.user.username}"


class Tag(models.Model):
    """Тег для вопросов"""
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Название тега"
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Question(models.Model):
    """Модель вопроса"""
    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок"
    )
    text = models.TextField(
        verbose_name="Текст вопроса"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Автор"
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='questions',
        verbose_name="Теги"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    rating = models.IntegerField(
        default=0,
        verbose_name="Рейтинг"
    )

    # Используем кастомный менеджер
    objects = QuestionManager()

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('question_detail', args=[self.id])

    @property
    def likes_count(self):
        """Количество лайков"""
        return self.question_likes.filter(value=1).count()

    @property
    def dislikes_count(self):
        """Количество дизлайков"""
        return self.question_likes.filter(value=-1).count()


class Answer(models.Model):
    """Модель ответа"""
    text = models.TextField(
        verbose_name="Текст ответа"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Автор"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Вопрос"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    rating = models.IntegerField(
        default=0,
        verbose_name="Рейтинг"
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name="Правильный ответ"
    )

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        ordering = ['-rating', 'created_at']

    def __str__(self):
        return f"Ответ на {self.question.title[:50]}"

    @property
    def likes_count(self):
        """Количество лайков"""
        return self.answer_likes.filter(value=1).count()

    @property
    def dislikes_count(self):
        """Количество дизлайков"""
        return self.answer_likes.filter(value=-1).count()


class QuestionLike(models.Model):
    """Лайк/дизлайк вопроса"""
    LIKE = 1
    DISLIKE = -1

    VALUE_CHOICES = [
        (LIKE, "Нравится"),
        (DISLIKE, "Не нравится"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='question_likes',
        verbose_name="Пользователь"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='question_likes',
        verbose_name="Вопрос"
    )
    value = models.SmallIntegerField(
        choices=VALUE_CHOICES,
        verbose_name="Оценка"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата оценки"
    )

    class Meta:
        verbose_name = "Оценка вопроса"
        verbose_name_plural = "Оценки вопросов"
        # Ограничение: один пользователь - один голос за вопрос
        unique_together = [['user', 'question']]

    def __str__(self):
        return f"{self.user.username}: {self.get_value_display()} вопроса {self.question.id}"


class AnswerLike(models.Model):
    """Лайк/дизлайк ответа"""
    LIKE = 1
    DISLIKE = -1

    VALUE_CHOICES = [
        (LIKE, "Нравится"),
        (DISLIKE, "Не нравится"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='answer_likes',
        verbose_name="Пользователь"
    )
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='answer_likes',
        verbose_name="Ответ"
    )
    value = models.SmallIntegerField(
        choices=VALUE_CHOICES,
        verbose_name="Оценка"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата оценки"
    )

    class Meta:
        verbose_name = "Оценка ответа"
        verbose_name_plural = "Оценки ответов"
        # Ограничение: один пользователь - один голос за ответ
        unique_together = [['user', 'answer']]

    def __str__(self):
        return f"{self.user.username}: {self.get_value_display()} ответа {self.answer.id}"

def avatar_upload_path(instance, filename):
    """Генерирует уникальный путь для аватарки"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f'avatars/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="profile"
    )
    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
        verbose_name="Аватар",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])]
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата регистрации"
    )
