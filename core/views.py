from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from datetime import datetime


def home_view(request):
    current_hour = datetime.now().hour

    if 5 <= current_hour < 12:
        greeting = 'おはようございます'
    elif 12 <= current_hour < 18:
        greeting = 'こんにちは'
    else:
        greeting = 'こんばんわ'

    return render(request, 'core/home.html', {'greeting': greeting})

def sq_detail(request):
    return render(request, 'core/sq_detail.html')

def about_view(request):
    return render(request, 'core/about.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})