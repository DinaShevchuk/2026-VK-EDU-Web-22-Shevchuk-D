from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Count
from .models import Question, Tag, Answer

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
    return render(request, 'one_question.html', context)
