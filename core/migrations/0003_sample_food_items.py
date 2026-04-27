from django.db import migrations


def create_sample_foods(apps, schema_editor):
    FoodItem = apps.get_model("core", "FoodItem")
    if FoodItem.objects.exists():
        return
    FoodItem.objects.bulk_create(
        [
            FoodItem(
                name="Cereal", calories_per_serving=400, serving_unit="bowl"
            ),
            FoodItem(
                name="Hamburger", calories_per_serving=250, serving_unit="each"
            ),
            FoodItem(
                name="Turkey", calories_per_serving=1294, serving_unit="plate"
            ),
            FoodItem(
                name="Chips", calories_per_serving=150, serving_unit="serving"
            ),
            FoodItem(
                name="CandyBar", calories_per_serving=120, serving_unit="bar"
            ),
        ]
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_userprofile_dashboard_fields"),
    ]

    operations = [
        migrations.RunPython(create_sample_foods, noop_reverse),
    ]
