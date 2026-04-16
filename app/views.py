import copy
import random
from tempfile import template
from tkinter.constants import CURRENT

from django.shortcuts import render, redirect
from django.http import HttpResponse

QUESTION = [
    {
    'title': f'TITLE {i}',
    'id': i,
    'text': f'a lot of text {i}',
    'answer_count': 2,
    'tags': ['darkchocolate', 'antioxidants', 'richflavor', 'health', 'cacao'],
    'author_id': i%5,
    } for i in range(0, 30)
]

ANSWER = [
    {
        'name': f'Name {i}',
        'id': i,
        'text': f'ans {i}',
        'ans_question': random.randint(0, 30),
        'author_id': i%5,
    } for i in range(0, 60)
]

USERS = [
    {
        'username': f'Name {i}',
        'id': i,
        'email': f'email{i}@email.com',
        'nickname': f'Nick{i}',
        'password': f'{i}{i}{i}',
        'avatar': 'ava3.jpg',
    } for i in range(0, 6)
]

CURRENT_USER = USERS[0]

def index(request):
    return render(
        request, 'index.html',
        context={'questions': QUESTION, 'user': CURRENT_USER}
    )

def hot(request):
    hot_question = copy.deepcopy(QUESTION)
    hot_question.reverse()
    return render(
        request, 'hot.html',
        context={'questions': hot_question, 'user': CURRENT_USER}
    )

def question(request, question_id):
    one_question = QUESTION[question_id]
    question_answers = [ans for ans in ANSWER if ans['ans_question'] == question_id]
    return render(
        request, 'one_question.html',
        context={'question': one_question, 'answers': question_answers, 'user': CURRENT_USER}
    )

def tag(request, tag_word):
    tag_list = [q for q in QUESTION if tag_word in q['tags']]
    return render(
        request, 'tag.html',
        context={'tag': tag_word, 'tag_list': tag_list, 'user': CURRENT_USER}
    )


def login_v(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        for user in USERS:
            if user['username'] == username and user['password'] == password:
                global CURRENT_USER
                CURRENT_USER = user
                return redirect('index')
    return render(request, 'login.html')