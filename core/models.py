from django.db import models


class AppUser(models.Model):
    ROLE_CHOICES = [
        ("CUSTOMER", "Customer"),
        ("ADMIN", "Admin"),
    ]

    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="CUSTOMER")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    ACTIVITY_CHOICES = [
        ("MILD", "Mild"),
        ("MODERATE", "Moderate"),
        ("SEVERE", "Severe"),
    ]

    user = models.OneToOneField(AppUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150, blank=True, default="")
    height_cm = models.FloatField()
    weight_kg = models.FloatField()
    daily_calorie_goal = models.FloatField(default=2500)
    notes = models.TextField(blank=True, default="")
    age = models.IntegerField(null=True, blank=True)
    activity_level = models.CharField(
        max_length=50,
        choices=ACTIVITY_CHOICES,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.email} profile"


class FoodItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    calories_per_serving = models.FloatField()
    serving_unit = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class MealLog(models.Model):
    MEAL_TYPE_CHOICES = [
        ("BREAKFAST", "Breakfast"),
        ("LUNCH", "Lunch"),
        ("DINNER", "Dinner"),
        ("SNACK", "Snack"),
    ]

    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    meal_time = models.DateTimeField()

    def __str__(self):
        return f"{self.user.email} - {self.meal_type}"


class MealLogItem(models.Model):
    meal = models.ForeignKey(MealLog, on_delete=models.CASCADE)
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.FloatField()
    calculated_calories = models.FloatField()

    def __str__(self):
        return f"{self.food.name} x {self.quantity}"