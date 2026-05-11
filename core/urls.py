from django.urls import path

from . import views

urlpatterns = [
    path('', views.homepage, name='home'),
    path('homepage/', views.homepage, name='homepage'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('historyrecord/', views.history_record, name='historyrecord'),
    path('add-meal/', views.add_meal, name='add_meal'),
]
