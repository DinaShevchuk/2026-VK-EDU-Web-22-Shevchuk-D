from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from app.models import Profile

def login_view(request):
    next_url = request.GET.get('next', reverse('app:index'))

    # Проверка на open redirect
    if next_url.startswith(('http://', 'https://', '//')):
        next_url = reverse('app:index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(next_url)
        else:
            return render(request, 'core/login.html', {'error': 'Invalid username or password'})

    return render(request, 'core/login.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Проверки
        if password != confirm_password:
            return render(request, 'core/signup.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'core/signup.html', {'error': 'Username already exists'})

        if User.objects.filter(email=email).exists():
            return render(request, 'core/signup.html', {'error': 'Email already exists'})

        # Создаем пользователя
        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.get_or_create(user=user)

        # Автоматически логиним
        login(request, user)
        return redirect('app:index')

    return render(request, 'core/signup.html')

def logout_view(request):
    next_url = request.GET.get('next', reverse('app:index'))

    if next_url.startswith(('http://', 'https://', '//')):
        next_url = reverse('app:index')

    logout(request)
    return redirect(next_url)

@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('core:profile')

    return render(request, 'core/profile.html', {'user': request.user})
