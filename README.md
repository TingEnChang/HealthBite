# HealthBite

A **Django** web app for meal and calorie tracking: sign up / sign in, a daily dashboard, log meals, browse history by date, progress charts, goals, and profile settings. Development uses **SQLite**.

## Stack

- Python 3.10+ (recommended)
- Django 4.2 (see comment in `DjangoProject1/settings.py`)
- SQLite (`db.sqlite3`)

## Features and routes

| Path | Description |
|------|-------------|
| `/` | Home: today’s meal lines, calorie total, notes |
| `/login/`, `/register/` | Sign in and sign up |
| `/add-meal/` | Log a meal (food, meal type, quantity) |
| `/historyrecord/` | Meal history for a selected date |
| `/progress/` | ~7-day calorie trend vs goal |
| `/goals/` | Goal-related summary |
| `/my-info/` | Profile, change password, delete account |
| `/logout/` | Sign out |
| `/admin/` | Django admin (superuser required) |

Auth uses a **session** (`user_id`). Application users are **`AppUser`** records, separate from Django’s built-in `User`.

## Local setup

### 1. Virtual environment (recommended)

```bash
cd HealthBite
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

There is no `requirements.txt` in the repo yet; install Django 4.2 to match settings:

```bash
pip install "Django>=4.2,<5"
```

### 3. Apply migrations

```bash
python3 manage.py migrate
```

### 4. Create an admin user (optional, for `/admin/`)

```bash
python3 manage.py createsuperuser
```

### 5. Run the dev server

```bash
python3 manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

## Admin and data

- Admin URL: **http://127.0.0.1:8000/admin/**
- Under **Core**, you can inspect **`AppUser`**, **`UserProfile`**, **`MealLog`**, **`MealLogItem`**, **`FoodItem`**, etc.
- If the meal form has no foods, add **`FoodItem`** rows in admin, or use any migrations/fixtures the project provides.

## Project layout (short)

```
HealthBite/
├── manage.py
├── DjangoProject1/          # project settings, root URLconf
├── core/                    # main app: models, views, urls, admin, static
├── templates/core/          # HTML templates
└── db.sqlite3               # local SQLite (do not commit sensitive DBs to public repos)
```

## Development notes

- **`DEBUG = True`** and the default **`SECRET_KEY`** are for local use only. Before production, follow the [Django deployment checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/).
- Sign-up / sign-in is a **demo-style** flow: passwords are stored in a **`password_hash`** field as plain text for this course-style app, not production-grade hashing. Do not deploy as-is.


