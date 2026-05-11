from collections import defaultdict
from datetime import timedelta

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date

from .models import AppUser, FoodItem, MealLog, MealLogItem, UserProfile

ACTIVITY_TO_FACTOR = {
    "MILD": 1.2,
    "MODERATE": 1.55,
    "SEVERE": 1.9,
    None: 1.375,
}


def _require_login_user(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None, None, redirect("/login/")
    user = get_object_or_404(AppUser, pk=user_id)
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "height_cm": 170,
            "weight_kg": 70,
            "full_name": user.email.split("@")[0].title(),
            "daily_calorie_goal": 2500,
        },
    )
    return user, profile, None


def _highest_meal_type_today(user_id, today):
    items = (
        MealLogItem.objects.filter(meal__user_id=user_id, meal__meal_time__date=today)
        .select_related("meal")
    )
    by_type = defaultdict(float)
    for item in items:
        by_type[item.meal.meal_type] += item.calculated_calories
    if not by_type:
        return None, 0
    best_type = max(by_type, key=by_type.get)
    return best_type, by_type[best_type]


def _chart_data(user_id, end_date, days=7):
    out = []
    for i in range(days - 1, -1, -1):
        d = end_date - timedelta(days=i)
        t = (
            MealLogItem.objects.filter(
                meal__user_id=user_id, meal__meal_time__date=d
            ).aggregate(s=Sum("calculated_calories"))["s"]
            or 0
        )
        out.append(
            {
                "date": d,
                "label": d.strftime("%a"),
                "total": float(t),
            }
        )
    return out


def _chart_svg_points(chart, max_v, w=300, h=120, pad=20):
    if not chart or max_v <= 0:
        return ""
    n = len(chart)
    if n < 1:
        return ""
    inner_w = w - 2 * pad
    inner_h = h - 2 * pad
    parts = []
    for i, c in enumerate(chart):
        v = float(c["total"])
        x = pad + (i / max(1, n - 1)) * inner_w if n > 1 else pad + inner_w / 2
        y = pad + inner_h * (1.0 - (v / max_v))
        parts.append(f"{x:.1f},{y:.1f}")
    return " ".join(parts)


def _goal_line_y(goal_val, max_v, w=300, h=120, pad=20):
    if max_v <= 0:
        return (h - pad) / 2.0
    inner_h = h - 2 * pad
    y = pad + inner_h * (1.0 - (float(goal_val) / max_v))
    return y


def _avg_calories_in_range(user_id, start_date, end_date):
    total = 0.0
    count_days = 0
    d = start_date
    while d <= end_date:
        day_sum = (
            MealLogItem.objects.filter(
                meal__user_id=user_id, meal__meal_time__date=d
            ).aggregate(s=Sum("calculated_calories"))["s"]
        )
        if day_sum is not None:
            total += float(day_sum)
        count_days += 1
        d += timedelta(days=1)
    if count_days == 0:
        return 0.0
    return total / count_days


def homepage(request):
    _u, profile, err = _require_login_user(request)
    if err:
        return err

    if request.method == "POST" and "save_notes" in request.POST:
        profile.notes = request.POST.get("notes", "")
        profile.save()
        messages.success(request, "Notes saved.")
        return redirect("home")

    user_id = request.session["user_id"]
    today = timezone.now().date()
    q = (
        MealLogItem.objects.filter(
            meal__user_id=user_id, meal__meal_time__date=today
        )
        .select_related("meal", "food")
        .order_by("meal__meal_time", "id")
    )

    total = (
        MealLogItem.objects.filter(
            meal__user_id=user_id, meal__meal_time__date=today
        ).aggregate(s=Sum("calculated_calories"))["s"]
    )
    total = float(total) if total is not None else 0.0
    goal = float(profile.daily_calorie_goal)
    over = max(0.0, total - goal)
    h_type, h_cal = _highest_meal_type_today(user_id, today)
    h_label = dict(MealLog.MEAL_TYPE_CHOICES).get(h_type, "—") if h_type else "—"

    return render(
        request,
        "core/homepage.html",
        {
            "nav_active": "home",
            "profile": profile,
            "meal_items": q,
            "total_calories": total,
            "daily_goal": goal,
            "calories_over_goal": over,
            "highest_meal_label": h_label,
            "highest_meal_cals": h_cal,
        },
    )


def progress_view(request):
    _u, profile, err = _require_login_user(request)
    if err:
        return err
    user_id = request.session["user_id"]
    if request.method == "POST" and "save_goals" in request.POST:
        try:
            g = float(request.POST.get("daily_calorie_goal", "2500"))
            profile.daily_calorie_goal = g
            profile.save()
            messages.success(request, "Goals updated.")
        except ValueError:
            messages.error(request, "Invalid goal value.")
        return redirect("progress")

    end = timezone.now().date()
    chart = _chart_data(user_id, end, 7)
    values = [c["total"] for c in chart]
    max_v = max(values + [float(profile.daily_calorie_goal), 1.0])
    chart_line = _chart_svg_points(chart, max_v)
    goal_y = _goal_line_y(profile.daily_calorie_goal, max_v)
    chart_end_cx, chart_end_cy = 20.0, 100.0
    if chart and max_v > 0:
        w, h, pad = 300, 120, 20
        inner_w = w - 2 * pad
        inner_h = h - 2 * pad
        n = len(chart)
        i = n - 1
        v = float(chart[i]["total"])
        chart_end_cx = pad + (i / max(1, n - 1)) * inner_w if n > 1 else pad + inner_w / 2
        chart_end_cy = pad + inner_h * (1.0 - (v / max_v))

    w_start = end - timedelta(days=6)
    m_start = end - timedelta(days=29)
    cur_day = _avg_calories_in_range(user_id, w_start, end)
    cur_week = _avg_calories_in_range(user_id, end - timedelta(days=6), end) * 7
    cur_month = _avg_calories_in_range(user_id, m_start, end) * 30

    g_day = float(profile.daily_calorie_goal)
    g_week = g_day * 7
    g_month = g_day * 30

    return render(
        request,
        "core/progress.html",
        {
            "nav_active": "progress",
            "profile": profile,
            "chart": chart,
            "chart_max": max_v,
            "chart_svg_line": chart_line,
            "chart_goal_y": goal_y,
            "chart_end_cx": chart_end_cx,
            "chart_end_cy": chart_end_cy,
            "goal_daily": g_day,
            "goal_weekly": g_week,
            "goal_monthly": g_month,
            "current_daily_avg": cur_day,
            "current_weekly": cur_week,
            "current_monthly": cur_month,
        },
    )


def goals_view(request):
    _u, profile, err = _require_login_user(request)
    if err:
        return err
    user_id = request.session["user_id"]
    if request.method == "POST" and "save_goals" in request.POST:
        try:
            g = float(request.POST.get("daily_calorie_goal", "2500"))
            profile.daily_calorie_goal = g
            profile.save()
            messages.success(request, "Goals updated.")
        except ValueError:
            messages.error(request, "Invalid goal value.")
        return redirect("goals")

    end = timezone.now().date()
    w_start = end - timedelta(days=6)
    m_start = end - timedelta(days=29)
    cur_day = _avg_calories_in_range(user_id, w_start, end)
    cur_week = _avg_calories_in_range(user_id, end - timedelta(days=6), end) * 7
    cur_month = _avg_calories_in_range(user_id, m_start, end) * 30
    g_day = float(profile.daily_calorie_goal)
    g_week = g_day * 7
    g_month = g_day * 30

    return render(
        request,
        "core/goals.html",
        {
            "nav_active": "goals",
            "profile": profile,
            "goal_daily": g_day,
            "goal_weekly": g_week,
            "goal_monthly": g_month,
            "current_daily_avg": cur_day,
            "current_weekly": cur_week,
            "current_monthly": cur_month,
        },
    )


def my_info(request):
    user, profile, err = _require_login_user(request)
    if err:
        return err

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "update":
            profile.full_name = request.POST.get("full_name", "").strip()
            try:
                profile.age = int(request.POST.get("age") or 0) or None
            except ValueError:
                profile.age = None
            try:
                profile.height_cm = float(request.POST.get("height_cm", "170"))
                profile.weight_kg = float(request.POST.get("weight_kg", "70"))
            except ValueError:
                messages.error(request, "Height and weight must be numbers.")
                return redirect("my_info")
            profile.activity_level = request.POST.get("activity_level") or None
            profile.save()
            messages.success(request, "Profile updated.")
            return redirect("my_info")
        if action == "reset_password":
            new_pw = request.POST.get("new_password", "")
            if len(new_pw) < 1:
                messages.error(request, "Enter a new password.")
                return redirect("my_info")
            user.password_hash = new_pw
            user.save()
            messages.success(request, "Password has been changed.")
            return redirect("my_info")
        if action == "delete":
            request.session.flush()
            user.delete()
            messages.info(request, "Your account was deleted.")
            return redirect("login")
        return redirect("my_info")

    factor = ACTIVITY_TO_FACTOR.get(profile.activity_level, 1.375)

    return render(
        request,
        "core/my_info.html",
        {
            "nav_active": "my_info",
            "user": user,
            "profile": profile,
            "activity_factor": factor,
        },
    )


def login_view(request):
    if request.session.get("user_id"):
        return redirect("home")
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""
        u = AppUser.objects.filter(email=email, password_hash=password).first()
        if u:
            request.session["user_id"] = u.id
            return redirect("home")
        return render(
            request,
            "core/login.html",
            {
                "login_error": "Invalid email or password.",
                "email_prefill": email,
            },
        )

    return render(request, "core/login.html", {})


def register_view(request):
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""
        name = (request.POST.get("full_name") or "").strip()
        try:
            age = int(request.POST.get("age") or 0) or None
        except ValueError:
            age = None
        try:
            height = float(request.POST.get("height_cm", "0"))
            weight = float(request.POST.get("weight_kg", "0"))
        except ValueError:
            messages.error(request, "Height and weight must be numbers.")
            return render(request, "core/register.html")
        activity = request.POST.get("activity_level") or None
        if not email or not password or height <= 0 or weight <= 0:
            messages.error(
                request, "Please fill email, password, height, and weight (positive)."
            )
            return render(request, "core/register.html")
        try:
            with transaction.atomic():
                u = AppUser.objects.create(
                    email=email,
                    password_hash=password,
                )
                UserProfile.objects.create(
                    user=u,
                    full_name=name,
                    height_cm=height,
                    weight_kg=weight,
                    age=age,
                    activity_level=activity,
                    daily_calorie_goal=2500,
                )
        except IntegrityError:
            messages.error(request, "This email is already registered.")
            return render(request, "core/register.html")
        return redirect("login")
    return render(request, "core/register.html")


def history_record(request):
    _u, _profile, err = _require_login_user(request)
    if err:
        return err
    user_id = request.session["user_id"]
    selected_date = parse_date(request.GET.get("date", "")) or timezone.now().date()

    meals = (
        MealLogItem.objects.filter(
            meal__user_id=user_id,
            meal__meal_time__date=selected_date,
        )
        .select_related("meal", "food")
        .order_by("meal__meal_time")
    )

    total_calories = (
        meals.aggregate(Sum("calculated_calories"))["calculated_calories__sum"] or 0
    )

    return render(
        request,
        "core/historyrecord.html",
        {
            "nav_active": "history",
            "selected_date": selected_date,
            "meals": meals,
            "total_calories": total_calories,
        },
    )


def logout_view(request):
    request.session.flush()
    return redirect("login")


def add_meal(request):
    _u, profile, err = _require_login_user(request)
    if err:
        return err
    user_id = request.session["user_id"]
    if request.method == "POST":
        food_id = request.POST.get("food")
        meal_type = request.POST.get("meal_type") or "LUNCH"
        if meal_type not in dict(MealLog.MEAL_TYPE_CHOICES):
            meal_type = "LUNCH"
        try:
            quantity = float(request.POST.get("quantity", "0"))
        except ValueError:
            messages.error(request, "Invalid quantity.")
            return redirect("add_meal")
        if quantity <= 0:
            messages.error(request, "Quantity must be positive.")
            return redirect("add_meal")
        food = get_object_or_404(FoodItem, pk=food_id)
        meal = MealLog.objects.create(
            user_id=user_id,
            meal_type=meal_type,
            meal_time=timezone.now(),
        )
        MealLogItem.objects.create(
            meal=meal,
            food=food,
            quantity=quantity,
            calculated_calories=food.calories_per_serving * quantity,
        )
        return redirect("home")
    foods = FoodItem.objects.all().order_by("name")
    return render(
        request,
        "core/add_meal.html",
        {
            "nav_active": "add_meal",
            "profile": profile,
            "foods": foods,
            "meal_type_choices": MealLog.MEAL_TYPE_CHOICES,
        },
    )
