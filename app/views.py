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
        'username': f'Guest',
        'id': 0,
        'email': f'@email.com',
        'password': f'',
        'avatar': 'avatar.png',
    } ,
    {
        'username': f'Name 1',
        'id': 1,
        'email': f'email1@email.com',
        'nickname': f'Nick1',
        'password': f'111',
        'avatar': 'ava3.jpg',
    } ,
{
        'username': f'Name 2',
        'id': 2,
        'email': f'email2@email.com',
        'nickname': f'Nick2',
        'password': f'222',
        'avatar': 'ava3.jpg',
    } ,
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
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"login {username}, {password}")
        for user in USERS:
            if user['username'] == username and user['password'] == password:
                global CURRENT_USER
                CURRENT_USER = user
                print(f"login {username}")
                return redirect('index')
        error = "Wrong username or password"
        print("login error")
    return render(request, 'login.html',{'user': CURRENT_USER, 'error': error})

def logout_v(request):
    global CURRENT_USER
    CURRENT_USER = USERS[0]
    print("logout user")
    return redirect('index')

def signup_v(request):
    error = None
    success = None
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        nickname = request.POST.get('nickname')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if not username or not email or not password:
            error = "Not All"
        elif password != confirm_password:
            error = "Passwords don't match"
        else:
            user_exists = False
            for user in USERS:
                if user['username'] == username:
                    user_exists = True
                    error = f"Username {username} already exists"
                    break
                if user['email'] == email:
                    user_exists = True
                    error = f"Email {email} already exists"
                    break
            if not user_exists:
                new_id = len(USERS)
                new_user = {
                    'username': username,
                    'email': email,
                    'nickname': nickname if nickname else username,
                    'password': password,
                    'avatar': 'ava2.jpg',
                }
                USERS.append(new_user)
                global CURRENT_USER
                CURRENT_USER = new_user
                print(f"create new user {username}")
                return redirect('index')
    return render(request, 'signup.html',{'user': CURRENT_USER, 'error': error})