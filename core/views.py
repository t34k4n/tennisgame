from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

def home(request):
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('character_select')
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('character_select')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def guest_view(request):
    guest_user = User.objects.create_user(username=f'guest_{User.objects.count()}', password='guest')
    login(request, guest_user)
    return redirect('character_select')

def logout_view(request):
    logout(request)
    return redirect('home')

def character_select(request):
    if request.method == 'POST':
        selected = request.POST.get('character')
        request.session['character'] = selected
        return redirect('game')
    return render(request, 'character_select.html')

def game_view(request):
    return render(request, 'game.html')
