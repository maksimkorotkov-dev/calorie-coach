# Calorie Counter - Calorie Tracking Application

An application for tracking calories and maintaining a food diary. Helps calculate daily calorie intake and monitor nutrition and physical activity.

## Features

- **Calorie Calculator** - calculate daily calorie needs using the Mifflin-St Jeor formula
- **Food Diary** - log consumed foods and meals
- **Activity Tracking** - record physical exercises
- **Weekly Statistics** - track progress over the week
- **Macronutrients** - track proteins, fats, and carbohydrates

## Requirements

- Python 3.11+
- Django 5.2+

## Local Installation

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd calorie-counter
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment:
- **Windows**: `venv\Scripts\activate`
- **macOS/Linux**: `source venv/bin/activate`

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

The server will be available at: http://127.0.0.1:8000

Or run on a specific port:

```bash
python manage.py runserver 0.0.0.0:5000
```

### 6. Open the Application

Open your browser and navigate to:
```
http://localhost:8000
```

## Project Structure

```
calorie-counter/
├── calorie_counter/          # Django project settings
│   ├── settings.py           # Project configuration
│   ├── urls.py               # Main URL routes
│   └── wsgi.py               # WSGI application
├── tracker/                  # Main application
│   ├── models.py             # Data models
│   ├── views.py              # View logic
│   └── urls.py               # Application URL routes
├── templates/                # HTML templates
│   ├── base.html             # Base template
│   └── tracker/
│       ├── calculator.html   # Calculator page
│       └── diary.html        # Diary page
├── static/                   # Static files
│   └── style.css             # Application styles
├── main.py                   # Entry point
├── manage.py                 # Django CLI
└── db.sqlite3                # SQLite database
```

## Application Pages

| URL | Description |
|-----|-------------|
| `/` | Calorie Calculator - calculate daily intake |
| `/diary/` | Food Diary - log food and activities |

## Usage

### Calorie Calculator

1. Open the main page `/`
2. Enter your data: age, weight, height, gender
3. Select your activity level
4. Choose your goal (weight loss, maintenance, weight gain)
5. Click "Calculate"
6. Get your daily calorie target

### Food Diary

1. Navigate to `/diary/`
2. Select a date in the weekly calendar
3. Add foods from the list or create your own
4. Add physical activities
5. Track your progress in weekly statistics

## Food Database

The application contains 20 pre-loaded foods and meals with calorie and macronutrient data (proteins, fats, carbohydrates).

## Activity Database

10 pre-loaded types of physical activities with calorie burn calculations.

## Technologies

- **Backend**: Django 5.2
- **Database**: SQLite
- **Static Files**: WhiteNoise
- **Styling**: Pure CSS with eco-green color scheme
