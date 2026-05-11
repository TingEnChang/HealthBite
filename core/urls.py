from django.urls import path

from . import views

urlpatterns = [
    path('', views.homepage, name='home'),
    path('homepage/', views.homepage, name='homepage'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('progress/', views.progress_view, name='progress'),
    path('goals/', views.goals_view, name='goals'),
    path('my-info/', views.my_info, name='my_info'),
    path('logout/', views.logout_view, name='logout'),
    path('add-meal/', views.add_meal, name='add_meal'),
    path('historyrecord/', views.history_record, name='historyrecord'),
]
