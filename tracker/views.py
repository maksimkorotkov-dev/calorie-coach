from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date, timedelta
from .models import CalorieProfile, FoodEntry, ActivityEntry, PRESET_ACTIVITIES, FOOD_DATABASE


def get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def calculator(request):
    session_key = get_session_key(request)
    profile = CalorieProfile.objects.filter(session_key=session_key).first()
    
    if request.method == 'POST':
        try:
            age = int(request.POST.get('age', 25))
            weight = float(request.POST.get('weight', 70))
            height = float(request.POST.get('height', 170))
            gender = request.POST.get('gender', 'male')
            activity_level = request.POST.get('activity_level', 'moderate')
            goal = request.POST.get('goal', 'maintain')
            
            if profile:
                profile.age = age
                profile.weight = weight
                profile.height = height
                profile.gender = gender
                profile.activity_level = activity_level
                profile.goal = goal
                profile.daily_calorie_target = profile.calculate_target_calories()
                profile.save()
            else:
                profile = CalorieProfile.objects.create(
                    session_key=session_key,
                    age=age,
                    weight=weight,
                    height=height,
                    gender=gender,
                    activity_level=activity_level,
                    goal=goal
                )
                profile.daily_calorie_target = profile.calculate_target_calories()
                profile.save()
            
            messages.success(request, 'Calorie profile calculated successfully!')
            
        except (ValueError, TypeError) as e:
            messages.error(request, 'Please enter valid values.')
    
    context = {
        'profile': profile,
        'activity_choices': CalorieProfile.ACTIVITY_CHOICES,
        'goal_choices': CalorieProfile.GOAL_CHOICES,
    }
    return render(request, 'tracker/calculator.html', context)


def diary(request):
    session_key = get_session_key(request)
    profile = CalorieProfile.objects.filter(session_key=session_key).first()
    
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        try:
            selected_date = date.fromisoformat(selected_date_str)
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()
    
    # Handle week navigation
    week_offset = request.GET.get('week')
    if week_offset:
        try:
            selected_date = selected_date + timedelta(weeks=int(week_offset))
        except ValueError:
            pass
    
    week_start = selected_date - timedelta(days=selected_date.weekday())
    week_days = [week_start + timedelta(days=i) for i in range(7)]
    
    food_entries = FoodEntry.objects.filter(session_key=session_key, date=selected_date)
    activity_entries = ActivityEntry.objects.filter(session_key=session_key, date=selected_date)
    
    daily_target = profile.daily_calorie_target if profile else 2000
    day_consumed = sum(entry.calories for entry in food_entries)
    day_burned = sum(entry.calories_burned for entry in activity_entries)
    day_net = day_consumed - day_burned
    day_remaining = daily_target - day_net
    day_progress = min(100, max(0, (day_net / daily_target) * 100)) if daily_target > 0 else 0
    
    # Calculate macro targets
    macro_targets = profile.calculate_macro_targets() if profile else {
        'protein_target': 100,
        'fat_target': 67,
        'carbs_target': 225,
    }
    
    # Daily macros consumed
    day_protein = sum(entry.protein or 0 for entry in food_entries)
    day_fat = sum(entry.fat or 0 for entry in food_entries)
    day_carbs = sum(entry.carbs or 0 for entry in food_entries)
    
    weekly_stats = {
        'total_consumed': 0,
        'total_burned': 0,
        'total_protein': 0,
        'total_fat': 0,
        'total_carbs': 0,
        'days_goal_met': 0,
        'days_with_entries': 0,
    }
    
    for day in week_days:
        day_foods = FoodEntry.objects.filter(session_key=session_key, date=day)
        day_activities = ActivityEntry.objects.filter(session_key=session_key, date=day)
        
        consumed = sum(e.calories for e in day_foods)
        burned = sum(e.calories_burned for e in day_activities)
        net = consumed - burned
        
        weekly_stats['total_consumed'] += consumed
        weekly_stats['total_burned'] += burned
        weekly_stats['total_protein'] += sum(e.protein or 0 for e in day_foods)
        weekly_stats['total_fat'] += sum(e.fat or 0 for e in day_foods)
        weekly_stats['total_carbs'] += sum(e.carbs or 0 for e in day_foods)
        
        if consumed > 0 or burned > 0:
            weekly_stats['days_with_entries'] += 1
            if net <= daily_target:
                weekly_stats['days_goal_met'] += 1
    
    weekly_stats['total_net'] = weekly_stats['total_consumed'] - weekly_stats['total_burned']
    weekly_stats['goal_achieved'] = weekly_stats['days_goal_met'] >= 5
    
    products = [f for f in FOOD_DATABASE if f['type'] == 'product']
    dishes = [f for f in FOOD_DATABASE if f['type'] == 'dish']
    
    # Calculate weekly macro targets (daily * 7)
    weekly_macro_targets = {
        'protein_target': macro_targets['protein_target'] * 7,
        'fat_target': macro_targets['fat_target'] * 7,
        'carbs_target': macro_targets['carbs_target'] * 7,
    }
    
    # Calculate remaining macros for the week
    weekly_stats['protein_remaining'] = weekly_macro_targets['protein_target'] - weekly_stats['total_protein']
    weekly_stats['fat_remaining'] = weekly_macro_targets['fat_target'] - weekly_stats['total_fat']
    weekly_stats['carbs_remaining'] = weekly_macro_targets['carbs_target'] - weekly_stats['total_carbs']
    
    context = {
        'profile': profile,
        'selected_date': selected_date,
        'week_days': week_days,
        'week_start': week_start,
        'food_entries': food_entries,
        'activity_entries': activity_entries,
        'daily_target': daily_target,
        'day_consumed': day_consumed,
        'day_burned': day_burned,
        'day_net': day_net,
        'day_remaining': day_remaining,
        'day_progress': day_progress,
        'weekly_stats': weekly_stats,
        'weekly_macro_targets': weekly_macro_targets,
        'macro_targets': macro_targets,
        'day_protein': day_protein,
        'day_fat': day_fat,
        'day_carbs': day_carbs,
        'preset_activities': PRESET_ACTIVITIES,
        'products': products,
        'dishes': dishes,
        'today': date.today(),
    }
    return render(request, 'tracker/diary.html', context)


def add_food(request):
    if request.method == 'POST':
        session_key = get_session_key(request)
        selected_date = request.POST.get('date', str(date.today()))
        food_name = request.POST.get('food_name')
        quantity = int(request.POST.get('quantity', 100))
        
        food_item = next((f for f in FOOD_DATABASE if f['name'] == food_name), None)
        
        if food_item:
            calories = int(food_item['calories'] * quantity / 100)
            protein = int(food_item['protein'] * quantity / 100)
            fat = int(food_item['fat'] * quantity / 100)
            carbs = int(food_item['carbs'] * quantity / 100)
            
            FoodEntry.objects.create(
                session_key=session_key,
                date=selected_date,
                name=f"{food_item['name']} ({quantity}g)",
                calories=calories,
                protein=protein,
                fat=fat,
                carbs=carbs
            )
            messages.success(request, 'Food added successfully!')
        else:
            messages.error(request, 'Food item not found.')
        
        return redirect(f'/diary/?date={selected_date}')
    
    return redirect('diary')


def add_custom_food(request):
    if request.method == 'POST':
        session_key = get_session_key(request)
        selected_date = request.POST.get('date', str(date.today()))
        name = request.POST.get('name', '').strip()
        calories = int(request.POST.get('calories', 0))
        protein = request.POST.get('protein')
        fat = request.POST.get('fat')
        carbs = request.POST.get('carbs')
        
        if name and calories > 0:
            FoodEntry.objects.create(
                session_key=session_key,
                date=selected_date,
                name=name,
                calories=calories,
                protein=int(protein) if protein else None,
                fat=int(fat) if fat else None,
                carbs=int(carbs) if carbs else None
            )
            messages.success(request, 'Custom food added successfully!')
        else:
            messages.error(request, 'Please provide food name and calories.')
        
        return redirect(f'/diary/?date={selected_date}')
    
    return redirect('diary')


def delete_food(request, food_id):
    session_key = get_session_key(request)
    entry = get_object_or_404(FoodEntry, id=food_id, session_key=session_key)
    selected_date = entry.date
    entry.delete()
    messages.success(request, 'Entry deleted.')
    return redirect(f'/diary/?date={selected_date}')


def add_activity(request):
    if request.method == 'POST':
        session_key = get_session_key(request)
        selected_date = request.POST.get('date', str(date.today()))
        activity_name = request.POST.get('activity_name')
        duration = int(request.POST.get('duration', 30))
        
        activity = next((a for a in PRESET_ACTIVITIES if a['name'] == activity_name), None)
        
        if activity:
            calories_burned = int((activity['calories_per_30min'] / 30) * duration)
            
            ActivityEntry.objects.create(
                session_key=session_key,
                date=selected_date,
                name=activity_name,
                duration=duration,
                calories_burned=calories_burned
            )
            messages.success(request, 'Activity added successfully!')
        else:
            messages.error(request, 'Activity not found.')
        
        return redirect(f'/diary/?date={selected_date}')
    
    return redirect('diary')


def delete_activity(request, activity_id):
    session_key = get_session_key(request)
    entry = get_object_or_404(ActivityEntry, id=activity_id, session_key=session_key)
    selected_date = entry.date
    entry.delete()
    messages.success(request, 'Entry deleted.')
    return redirect(f'/diary/?date={selected_date}')
