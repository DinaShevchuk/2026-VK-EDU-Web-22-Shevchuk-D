from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from app.models import Profile, Question, Answer
from django.urls import reverse

class LoginForm(forms.Form):
    """Форма для авторизации"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class SignupForm(UserCreationForm):
    """Форма регистрации с валидацией пароля через AUTH_PASSWORD_VALIDATORS"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    nickname = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nickname'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm password'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Создаем профиль
            Profile.objects.get_or_create(user=user)
        return user


class ProfileForm(forms.ModelForm):
    """Форма редактирования профиля"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Profile
        fields = []  # Пока не добавляем avatar
        # fields = ('avatar',)  # Раскомментировать, когда добавите загрузку аватара

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['username'].initial = self.user.username
            self.fields['email'].initial = self.user.email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.exclude(pk=self.user.pk).filter(username=username).exists():
            raise ValidationError('Пользователь с таким именем уже существует')
        return username

    def save(self, commit=True):
        if self.user:
            self.user.username = self.cleaned_data['username']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        return super().save(commit)


class AskForm(forms.ModelForm):
    """Форма добавления вопроса"""
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tags (comma-separated)'}),
        help_text='Введите теги через запятую'
    )

    class Meta:
        model = Question
        fields = ('title', 'text')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Question title'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Question text', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author', None)
        super().__init__(*args, **kwargs)

    def clean_tags(self):
        tags_data = self.cleaned_data.get('tags', '')
        tag_names = [tag.strip().lower() for tag in tags_data.split(',') if tag.strip()]
        return tag_names

    def save(self, commit=True):
        question = super().save(commit=False)
        question.author = self.author
        if commit:
            question.save()
            # Обработка тегов
            from app.models import Tag
            tag_names = self.cleaned_data['tags']
            tags = []
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
            question.tags.set(tags)
        return question


class AnswerForm(forms.ModelForm):
    """Форма добавления ответа"""
    class Meta:
        model = Answer
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your answer...', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author', None)
        self.question = kwargs.pop('question', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        answer = super().save(commit=False)
        answer.author = self.author
        answer.question = self.question
        if commit:
            answer.save()
        return answer
