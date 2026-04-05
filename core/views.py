from django.shortcuts import render


def homepage(request):
    return render(request, 'core/homepage.html')


def login_view(request):
    return render(request, 'core/login.html')


def register_view(request):
    return render(request, 'core/register.html')


def history_record(request):
    return render(request, 'core/historyrecord.html')
