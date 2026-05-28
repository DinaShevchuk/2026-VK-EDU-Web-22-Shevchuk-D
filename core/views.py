# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from app.models import Profile
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import SignupForm, ProfileForm  # если используете формы

def login_view(request):
    next_url = request.GET.get('next', reverse('app:index'))

    # Правильная валидация next_url
    if not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = reverse('app:index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(next_url)
        else:
            return render(request, 'core/login.html', {
                'error': 'Invalid username or password',
                'next': next_url
            })

    return render(request, 'core/login.html', {'next': next_url})


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('app:index')
        else:
            return render(request, 'core/signup.html', {
                'form': form,
                'error': form.errors
            })
    else:
        form = SignupForm()

    return render(request, 'core/signup.html', {'form': form})


def logout_view(request):
    next_url = request.GET.get('next', reverse('app:index'))

    if not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = reverse('app:index')

    logout(request)
    return redirect(next_url)


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('core:profile')
    else:
        form = ProfileForm(user=request.user)

    return render(request, 'core/profile.html', {'form': form})
