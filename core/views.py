from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import AppUser
from .models import MealLog, MealLogItem, FoodItem
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.db.models import Sum

from .models import AppUser, FoodItem, MealLog, MealLogItem

def homepage(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('/login/')

    today = timezone.now().date()

    total = MealLogItem.objects.filter(
        meal__user_id=user_id,
        meal__meal_time__date=today
    ).aggregate(Sum('calculated_calories'))['calculated_calories__sum']

    return render(request, 'core/homepage.html', {
        'total_calories': total or 0
    })


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = AppUser.objects.filter(email=email, password_hash=password).first()

        if user:
            request.session['user_id'] = user.id
            return redirect('/homepage/')

        else:
            return HttpResponse("Invalid email or password")

    return render(request, 'core/login.html')


def register_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        AppUser.objects.create(
            email=email,
            password_hash=password
        )

        return redirect('/login/')

    return render(request, 'core/register.html')


def history_record(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('/login/')

    selected_date = parse_date(request.GET.get('date', '')) or timezone.now().date()

    meals = MealLogItem.objects.filter(
        meal__user_id=user_id,
        meal__meal_time__date=selected_date
    ).select_related('meal', 'food').order_by('meal__meal_time')

    total_calories = meals.aggregate(Sum('calculated_calories'))['calculated_calories__sum'] or 0

    return render(request, 'core/historyrecord.html', {
        'selected_date': selected_date,
        'meals': meals,
        'total_calories': total_calories
    })


def logout_view(request):
    request.session.flush()
    return redirect('/login/')



def add_meal(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('/login/')

    if request.method == "POST":
        food_id = request.POST.get("food")
        meal_type = request.POST.get("meal_type")
        quantity = float(request.POST.get("quantity"))

        food = FoodItem.objects.get(id=food_id)

        meal = MealLog.objects.create(
            user_id=user_id,
            meal_type=meal_type,
            meal_time=timezone.now()
        )

        MealLogItem.objects.create(
            meal=meal,
            food=food,
            quantity=quantity,
            calculated_calories=food.calories_per_serving * quantity
        )

        return redirect('/homepage/')

    foods = FoodItem.objects.all()
    return render(request, 'core/add_meal.html', {
        'foods': foods,
        'meal_types': MealLog.MEAL_TYPE_CHOICES
    })
