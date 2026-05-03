from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import AppUser
from .models import MealLog, MealLogItem, FoodItem
from django.utils import timezone
from django.db.models import Sum
from .models import UserProfile


from .models import AppUser, FoodItem, MealLog, MealLogItem

from .models import UserProfile

def homepage(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('/login/')

    today = timezone.now().date()

    total = MealLogItem.objects.filter(
        meal__user_id=user_id,
        meal__meal_time__date=today
    ).aggregate(Sum('calculated_calories'))['calculated_calories__sum'] or 0


    profile = UserProfile.objects.filter(user_id=user_id).first()

    recommended = None

    if profile:

        recommended = profile.weight_kg * 30

    return render(request, 'core/homepage.html', {
        'total_calories': total,
        'recommended': recommended
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

    meal_items = MealLogItem.objects.filter(
        meal__user_id=user_id
    ).order_by('-meal__meal_time')

    return render(request, 'core/historyrecord.html', {
        'meal_items': meal_items
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
        quantity = float(request.POST.get("quantity"))

        food = FoodItem.objects.get(id=food_id)

        meal = MealLog.objects.create(
            user_id=user_id,
            meal_type="LUNCH",
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
    return render(request, 'core/add_meal.html', {'foods': foods})

def myinfo_view(request):
        user_id = request.session.get('user_id')

        if not user_id:
            return redirect('/login/')

        if request.method == "POST":
            height = request.POST.get("height")
            weight = request.POST.get("weight")
            age = request.POST.get("age")
            activity = request.POST.get("activity")


            profile, created = UserProfile.objects.get_or_create(user_id=user_id)

            profile.height_cm = height
            profile.weight_kg = weight
            profile.age = age if age else None
            profile.activity_level = activity if activity else None
            profile.save()

            return HttpResponse("Profile saved")

        return render(request, 'core/myinfo.html')

