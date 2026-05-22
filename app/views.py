from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Question, Tag, Answer, Profile

def paginate(request, queryset, per_page=10):
    page_number = request.GET.get('page', 1)
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(page_number)

def get_popular_tags():
    return Tag.objects.annotate(
        questions_count=Count('questions')
    ).order_by('-questions_count')[:10]

def index(request):
    questions = Question.objects.get_new().select_related('author').prefetch_related('tags')
    page = paginate(request, questions)
    context = {
        'page': page,
        'popular_tags': get_popular_tags(),
    }
    return render(request, 'index.html', context)

def hot(request):
    questions = Question.objects.get_best().select_related('author').prefetch_related('tags')
    page = paginate(request, questions)
    context = {
        'page': page,
        'popular_tags': get_popular_tags(),
    }
    return render(request, 'hot.html', context)

def tag(request, tag_name):
    get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.get_by_tag(tag_name).select_related('author').prefetch_related('tags')
    page = paginate(request, questions)
    context = {
        'page': page,
        'popular_tags': get_popular_tags(),
        'tag_name': tag_name,
    }
    return render(request, 'tag.html', context)

def question_detail(request, question_id):
    question = get_object_or_404(
        Question.objects.select_related('author').prefetch_related('tags'),
        id=question_id
    )
    answers = question.answers.select_related('author').all()
    answers_page = paginate(request, answers, per_page=5)
    context = {
        'question': question,
        'answers_page': answers_page,
        'popular_tags': get_popular_tags(),
    }
    return render(request, 'question.html', context)

# ========== ФУНКЦИИ ДЛЯ АВТОРИЗАЦИИ ==========

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'app:index')
            return redirect(next_url)
        else:
            context = {
                'error': 'Неверное имя пользователя или пароль',
                'popular_tags': get_popular_tags(),
            }
            return render(request, 'login.html', context)

    context = {
        'popular_tags': get_popular_tags(),
    }
    return render(request, 'login.html', context)

def user_logout(request):
    logout(request)
    return redirect('app:index')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        nickname = request.POST.get('nickname')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Проверки
        if password != confirm_password:
            context = {'error': 'Пароли не совпадают', 'popular_tags': get_popular_tags()}
            return render(request, 'signup.html', context)

        if User.objects.filter(username=username).exists():
            context = {'error': 'Пользователь с таким именем уже существует', 'popular_tags': get_popular_tags()}
            return render(request, 'signup.html', context)

        if User.objects.filter(email=email).exists():
            context = {'error': 'Пользователь с таким email уже существует', 'popular_tags': get_popular_tags()}
            return render(request, 'signup.html', context)

        # Создаём пользователя
        user = User.objects.create_user(username=username, email=email, password=password)

        # Создаём профиль
        Profile.objects.get_or_create(user=user)

        # Автоматически логиним
        login(request, user)
        return redirect('app:index')

    context = {'popular_tags': get_popular_tags()}
    return render(request, 'signup.html', context)

@login_required
def settings(request):
    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email', user.email)
        user.save()

        nickname = request.POST.get('nickname')
        if nickname:
            profile = user.profile
            # profile.nickname = nickname
            # profile.save()

        messages.success(request, 'Настройки сохранены!')
        return redirect('app:settings')

    context = {
        'popular_tags': get_popular_tags(),
    }
    return render(request, 'settings.html', context)
