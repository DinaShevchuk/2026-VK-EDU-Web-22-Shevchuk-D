import copy
from tempfile import template

from django.shortcuts import render
from django.http import HttpResponse

QUESTION = [
    {
    'title': f'TITLE {i}',
    'id': i,
    'text': f'a lot of text {i}'
    } for i in range(1, 30)
]


def index(request):
    return render(
        request, 'index.html',
        context={'questions': QUESTION}
    )

def hot(request):
    hot_question = copy.deepcopy(QUESTION)
    hot_question.reverse()
    return render(
        request, 'hot.html',
        context={'questions': hot_question}
    )

def question(request, question_id):
    one_question = QUESTION[question_id]
    return render(
        request, 'one_question.html',
        context={'question': one_question}
    )
