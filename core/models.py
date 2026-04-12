from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, default="CUSTOMER")
    created_at = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    height_cm = models.FloatField()
    weight_kg = models.FloatField()
    age = models.IntegerField(null=True, blank=True)
    activity_level = models.CharField(max_length=50, null=True, blank=True)

class FoodItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    calories_per_serving = models.FloatField()
    serving_unit = models.CharField(max_length=50)

class MealLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=20)
    meal_time = models.DateTimeField()

class MealLogItem(models.Model):
    meal = models.ForeignKey(MealLog, on_delete=models.CASCADE)
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.FloatField()
    calculated_calories = models.FloatField()