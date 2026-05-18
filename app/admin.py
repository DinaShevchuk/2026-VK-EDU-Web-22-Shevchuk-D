from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль'


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ['author', 'text', 'rating', 'is_correct']
    show_change_link = True


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    list_filter = []
    verbose_name = "Тег"
    verbose_name_plural = "Теги"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'rating', 'created_at']
    search_fields = ['title', 'text', 'author__username']
    list_filter = ['created_at', 'tags']
    raw_id_fields = ['author']
    filter_horizontal = ['tags']
    inlines = [AnswerInline]
    readonly_fields = ['rating']
    verbose_name = "Вопрос"
    verbose_name_plural = "Вопросы"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'author', 'rating', 'is_correct', 'created_at']
    search_fields = ['text', 'author__username', 'question__title']
    list_filter = ['is_correct', 'created_at']
    raw_id_fields = ['author', 'question']
    readonly_fields = ['rating']
    verbose_name = "Ответ"
    verbose_name_plural = "Ответы"


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'question', 'value', 'created_at']
    search_fields = ['user__username', 'question__title']
    list_filter = ['value', 'created_at']
    raw_id_fields = ['user', 'question']
    verbose_name = "Оценка вопроса"
    verbose_name_plural = "Оценки вопросов"


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'answer', 'value', 'created_at']
    search_fields = ['user__username']
    list_filter = ['value', 'created_at']
    raw_id_fields = ['user', 'answer']
    verbose_name = "Оценка ответа"
    verbose_name_plural = "Оценки ответов"


# Перерегистрируем User модель с кастомным админом
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Настройка заголовков админки
admin.site.site_header = "Панель управления AskMe"
admin.site.site_title = "AskMe Admin"
admin.site.index_title = "Добро пожаловать в AskMe"
