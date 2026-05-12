from django.contrib import admin

from .models import AppUser, FoodItem, MealLog, MealLogItem, UserProfile


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "calories_per_serving", "serving_unit")
    search_fields = ("name",)


@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "role", "created_at")
    search_fields = ("email",)
    ordering = ("-created_at",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "height_cm", "weight_kg", "daily_calorie_goal")
    search_fields = ("user__email", "full_name")
    raw_id_fields = ("user",)


class MealLogItemInline(admin.TabularInline):
    model = MealLogItem
    extra = 0


@admin.register(MealLog)
class MealLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "meal_type", "meal_time")
    list_filter = ("meal_type",)
    search_fields = ("user__email",)
    ordering = ("-meal_time",)
    inlines = (MealLogItemInline,)
    raw_id_fields = ("user",)


@admin.register(MealLogItem)
class MealLogItemAdmin(admin.ModelAdmin):
    list_display = ("id", "meal", "food", "quantity", "calculated_calories")
    list_filter = ("meal__meal_type",)
    search_fields = ("meal__user__email", "food__name")
    raw_id_fields = ("meal", "food")
