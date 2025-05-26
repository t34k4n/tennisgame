from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('guest/', views.guest_view, name='guest'),
    path('logout/', views.logout_view, name='logout'),
    path('character-select/', views.character_select, name='character_select'),
    path('game/', views.game_view, name='game'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('settings/', views.settings_view, name='settings'),
    path('game-mode/', views.game_mode_view, name='game_mode'),

    # admin panel
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/delete/<int:user_id>/', views.delete_user, name='delete_user'),

    # skor kaydetme endpointi
    path('save-match/', views.save_match, name='save_match'),

]
