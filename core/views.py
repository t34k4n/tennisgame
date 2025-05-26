from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import re
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import MatchResult


def home(request):
    return render(request, 'home.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        errors = {}

        if User.objects.filter(username=username).exists():
            errors['error_username'] = 'Username already exists'

        if User.objects.filter(email=email).exists():
            errors['error_email'] = 'Email already in use'

        if len(password) < 8 or not re.search(r'\d', password):
            errors['error'] = 'Password must be at least 8 characters and include a number'

        if password != password2:
            errors['error'] = 'Passwords do not match'

        if errors:
            return render(request, 'register.html', errors)

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('dashboard')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


def guest_view(request):
    guest_user = User.objects.create_user(username=f'guest_{User.objects.count()}', password='guest')
    login(request, guest_user)
    return redirect('dashboard')


def logout_view(request):
    logout(request)
    return redirect('home')


def character_select(request):
    characters = [
        {'char': 'red', 'color': 'red', 'speed': 33, 'power': 33, 'slowmo': 100},
        {'char': 'purple', 'color': 'purple', 'speed': 100, 'power': 33, 'slowmo': 33},
        {'char': 'green', 'color': 'lime', 'speed': 33, 'power': 100, 'slowmo': 33},
        {'char': 'blue', 'color': '#1e90ff', 'speed': 66, 'power': 66, 'slowmo': 66},
    ]

    if request.method == 'POST':
        c1 = request.POST.get('character1')
        c2 = request.POST.get('character2')

        if not c1 or not c2:
            return render(request, 'character_select.html', {
                'characters': characters,
                'error': 'Her iki oyuncu için de karakter seçmelisin.'
            })

        char_data = {
            "red": {"speed": 1, "power": 1, "slowmo": 3, "color": "red"},
            "blue": {"speed": 2, "power": 2, "slowmo": 2, "color": "#1e90ff"},
            "purple": {"speed": 3, "power": 1, "slowmo": 1, "color": "purple"},
            "green": {"speed": 1, "power": 3, "slowmo": 1, "color": "lime"},
        }

        stats1 = char_data.get(c1)
        stats2 = char_data.get(c2)

        request.session['character1'] = c1
        request.session['character2'] = c2
        request.session['speed1'] = stats1['speed']
        request.session['power1'] = stats1['power']
        request.session['slowmo1'] = stats1['slowmo']
        request.session['color1'] = stats1['color']
        request.session['speed2'] = stats2['speed']
        request.session['power2'] = stats2['power']
        request.session['slowmo2'] = stats2['slowmo']
        request.session['color2'] = stats2['color']

        return redirect('game')

    return render(request, 'character_select.html', { 'characters': characters })


def game_view(request):
    return render(request, 'game.html', {
        'slowmo1': request.session.get('slowmo1', 2),
        'slowmo2': request.session.get('slowmo2', 2),
        'color1': request.session.get('color1', 'red'),
        'color2': request.session.get('color2', 'white')
    })

def dashboard_view(request):
    recent_matches = []
    if request.user.is_authenticated:
        recent_matches = MatchResult.objects.filter(player=request.user).order_by('-created_at')[:5]
    return render(request, 'dashboard.html', {'matches': recent_matches})


@csrf_exempt
def save_match(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            MatchResult.objects.create(
                player=request.user,
                opponent=data.get('opponent', 'Unknown'),
                player_score=data.get('player_score', 0),
                opponent_score=data.get('opponent_score', 0)
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'unauthorized'}, status=401)


def settings_view(request):
    context = {}
    user = request.user

    if request.method == 'POST':
        if 'change_email' in request.POST:
            old_email = request.POST['old_email']
            new_email = request.POST['new_email']

            if user.email != old_email:
                context['email_error'] = "Old email doesn't match"
            elif User.objects.filter(email=new_email).exclude(username=user.username).exists():
                context['email_error'] = "New email is already in use"
            else:
                user.email = new_email
                user.save()
                context['email_success'] = "Email updated successfully"

        if 'change_password' in request.POST:
            old_password = request.POST['old_password']
            new_password = request.POST['new_password']
            confirm_password = request.POST['confirm_password']

            if not user.check_password(old_password):
                context['password_error'] = "Old password is incorrect"
            elif new_password != confirm_password:
                context['password_error'] = "New passwords do not match"
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                context['password_success'] = "Password updated successfully"

    return render(request, 'settings.html', context)


def game_mode_view(request):
    if request.method == 'POST':
        mode = request.POST.get('mode')
        request.session['mode'] = mode
        return redirect('character_select')
    return render(request, 'game_mode.html')


@user_passes_test(lambda u: u.is_staff)
def admin_panel(request):
    users = User.objects.exclude(is_superuser=True)
    return render(request, 'admin_panel.html', {'users': users})


@user_passes_test(lambda u: u.is_staff)
def delete_user(request, user_id):
    User.objects.filter(id=user_id).exclude(is_superuser=True).delete()
    return redirect('admin_panel')

def save_match(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        opponent = data.get('opponent', 'Unknown')
        player_score = data.get('player_score', 0)
        opponent_score = data.get('opponent_score', 0)

        MatchResult.objects.create(
            player=request.user,
            opponent=opponent,
            player_score=player_score,
            opponent_score=opponent_score
        )
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'unauthorized'}, status=401)