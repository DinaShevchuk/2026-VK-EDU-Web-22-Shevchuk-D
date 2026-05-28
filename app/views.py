# app/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from .models import Question, Tag, Answer, Profile
from core.forms import AskForm, AnswerForm  # Импортируем формы из core

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

# ========== НОВЫЕ ПРЕДСТАВЛЕНИЯ ДЛЯ ВОПРОСОВ И ОТВЕТОВ ==========

@login_required
def ask_question(request):
    """Добавление вопроса (только для авторизованных)"""
    if request.method == 'POST':
        form = AskForm(request.POST, author=request.user)
        if form.is_valid():
            question = form.save()
            return redirect('app:question_detail', question_id=question.id)
    else:
        form = AskForm()

    context = {
        'form': form,
        'popular_tags': get_popular_tags(),
    }
    return render(request, 'ask.html', context)

@login_required
def add_answer(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.method == 'POST':
        form = AnswerForm(request.POST, author=request.user, question=question)
        if form.is_valid():
            answer = form.save()
            # Перенаправляем с якорем на новый ответ
            return redirect(f"{reverse('app:question_detail', args=[question_id])}#answer-{answer.id}")
    else:
        form = AnswerForm()

    return render(request, 'add_answer.html', {
        'form': form,
        'question': question,
        'popular_tags': get_popular_tags(),
    })
