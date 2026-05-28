# app/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Count, Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from .models import Question, Tag, Answer, Profile
from core.forms import AskForm, AnswerForm  # Импортируем формы из core
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Question, Tag, Answer, Profile, QuestionLike, AnswerLike

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

@require_POST
@login_required
def like_question(request, question_id):
    """AJAX лайк/дизлайк вопроса"""
    try:
        question = Question.objects.get(id=question_id)
        value = int(request.POST.get('value', 0))

        if value not in [1, -1]:
            return JsonResponse({'error': 'Invalid value'}, status=400)

        # Проверяем, не лайкал ли уже пользователь
        existing_like = QuestionLike.objects.filter(user=request.user, question=question).first()

        if existing_like:
            if existing_like.value == value:
                # Удаляем лайк если тот же
                existing_like.delete()
            else:
                # Меняем лайк на противоположный
                existing_like.value = value
                existing_like.save()
        else:
            # Создаем новый лайк
            QuestionLike.objects.create(user=request.user, question=question, value=value)

        # Обновляем рейтинг
        rating_sum = question.question_likes.aggregate(Sum('value'))['value__sum'] or 0
        question.rating = rating_sum
        question.save()

        return JsonResponse({
            'success': True,
            'rating': question.rating,
            'likes_count': question.likes_count,
            'dislikes_count': question.dislikes_count
        })

    except Question.DoesNotExist:
        return JsonResponse({'error': 'Question not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
@login_required
def like_answer(request, answer_id):
    """AJAX лайк/дизлайк ответа"""
    try:
        answer = Answer.objects.get(id=answer_id)
        value = int(request.POST.get('value', 0))

        if value not in [1, -1]:
            return JsonResponse({'error': 'Invalid value'}, status=400)

        existing_like = AnswerLike.objects.filter(user=request.user, answer=answer).first()

        if existing_like:
            if existing_like.value == value:
                existing_like.delete()
            else:
                existing_like.value = value
                existing_like.save()
        else:
            AnswerLike.objects.create(user=request.user, answer=answer, value=value)

        rating_sum = answer.answer_likes.aggregate(Sum('value'))['value__sum'] or 0
        answer.rating = rating_sum
        answer.save()

        return JsonResponse({
            'success': True,
            'rating': answer.rating,
            'likes_count': answer.likes_count,
            'dislikes_count': answer.dislikes_count
        })

    except Answer.DoesNotExist:
        return JsonResponse({'error': 'Answer not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
@login_required
def mark_correct_answer(request, answer_id):
    """AJAX отметить правильный ответ"""
    try:
        answer = Answer.objects.get(id=answer_id)

        # Проверяем, что пользователь - автор вопроса
        if request.user != answer.question.author:
            return JsonResponse({'error': 'Only question author can mark correct answer'}, status=403)

        # Снимаем отметку со всех ответов этого вопроса
        Answer.objects.filter(question=answer.question).update(is_correct=False)

        # Отмечаем выбранный ответ как правильный
        answer.is_correct = True
        answer.save()

        return JsonResponse({
            'success': True,
            'answer_id': answer.id,
            'is_correct': answer.is_correct
        })

    except Answer.DoesNotExist:
        return JsonResponse({'error': 'Answer not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
