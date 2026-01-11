from django.db import models


class CalorieProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    ACTIVITY_CHOICES = [
        ('sedentary', 'Sedentary (little or no exercise)'),
        ('light', 'Light (exercise 1-3 days/week)'),
        ('moderate', 'Moderate (exercise 3-5 days/week)'),
        ('active', 'Active (exercise 6-7 days/week)'),
        ('very_active', 'Very Active (hard exercise daily)'),
    ]
    
    GOAL_CHOICES = [
        ('lose', 'Lose Weight'),
        ('maintain', 'Maintain Weight'),
        ('gain', 'Gain Weight'),
    ]
    
    age = models.IntegerField()
    weight = models.FloatField()
    height = models.FloatField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    goal = models.CharField(max_length=10, choices=GOAL_CHOICES)
    daily_calorie_target = models.IntegerField(null=True, blank=True)
    session_key = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile (age={self.age}, target={self.daily_calorie_target})"
    
    def calculate_bmr(self):
        if self.gender == 'male':
            return 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            return 10 * self.weight + 6.25 * self.height - 5 * self.age - 161
    
    def calculate_tdee(self):
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9,
        }
        bmr = self.calculate_bmr()
        return bmr * activity_multipliers.get(self.activity_level, 1.2)
    
    def calculate_target_calories(self):
        goal_adjustments = {
            'lose': -500,
            'maintain': 0,
            'gain': 500,
        }
        tdee = self.calculate_tdee()
        return int(tdee + goal_adjustments.get(self.goal, 0))
    
    def calculate_macro_targets(self):
        """
        Calculate daily macro targets (protein, fat, carbs) based on goal.
        Returns dict with protein_target, fat_target, carbs_target in grams.
        
        Macro ratios by goal:
        - Lose weight: High protein (35%), moderate fat (30%), lower carbs (35%)
        - Maintain: Balanced (25% protein, 30% fat, 45% carbs)
        - Gain weight: High protein (30%), moderate fat (25%), high carbs (45%)
        """
        calories = self.daily_calorie_target or self.calculate_target_calories()
        
        if self.goal == 'lose':
            protein_pct = 0.35
            fat_pct = 0.30
            carbs_pct = 0.35
        elif self.goal == 'gain':
            protein_pct = 0.30
            fat_pct = 0.25
            carbs_pct = 0.45
        else:  # maintain
            protein_pct = 0.25
            fat_pct = 0.30
            carbs_pct = 0.45
        
        # Calories per gram: protein=4, fat=9, carbs=4
        protein_target = int((calories * protein_pct) / 4)
        fat_target = int((calories * fat_pct) / 9)
        carbs_target = int((calories * carbs_pct) / 4)
        
        return {
            'protein_target': protein_target,
            'fat_target': fat_target,
            'carbs_target': carbs_target,
        }


class FoodEntry(models.Model):
    session_key = models.CharField(max_length=100, db_index=True)
    date = models.DateField()
    name = models.CharField(max_length=200)
    calories = models.IntegerField()
    protein = models.IntegerField(null=True, blank=True)
    fat = models.IntegerField(null=True, blank=True)
    carbs = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.calories} kcal)"


class ActivityEntry(models.Model):
    session_key = models.CharField(max_length=100, db_index=True)
    date = models.DateField()
    name = models.CharField(max_length=200)
    duration = models.IntegerField()
    calories_burned = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.duration} min, -{self.calories_burned} kcal)"


PRESET_ACTIVITIES = [
    {'name': 'Running', 'calories_per_30min': 300},
    {'name': 'Walking', 'calories_per_30min': 120},
    {'name': 'Cycling', 'calories_per_30min': 250},
    {'name': 'Swimming', 'calories_per_30min': 280},
    {'name': 'Yoga', 'calories_per_30min': 90},
    {'name': 'Weight Training', 'calories_per_30min': 180},
    {'name': 'Dancing', 'calories_per_30min': 200},
    {'name': 'HIIT', 'calories_per_30min': 350},
    {'name': 'Tennis', 'calories_per_30min': 220},
    {'name': 'Soccer', 'calories_per_30min': 280},
]


FOOD_DATABASE = [
    {'name': 'Chicken Breast', 'type': 'product', 'calories': 165, 'protein': 31, 'fat': 4, 'carbs': 0},
    {'name': 'Rice (white)', 'type': 'product', 'calories': 130, 'protein': 3, 'fat': 0, 'carbs': 28},
    {'name': 'Eggs', 'type': 'product', 'calories': 155, 'protein': 13, 'fat': 11, 'carbs': 1},
    {'name': 'Salmon', 'type': 'product', 'calories': 208, 'protein': 20, 'fat': 13, 'carbs': 0},
    {'name': 'Beef', 'type': 'product', 'calories': 250, 'protein': 26, 'fat': 17, 'carbs': 0},
    {'name': 'Cottage Cheese', 'type': 'product', 'calories': 98, 'protein': 11, 'fat': 4, 'carbs': 3},
    {'name': 'Greek Yogurt', 'type': 'product', 'calories': 59, 'protein': 10, 'fat': 0, 'carbs': 4},
    {'name': 'Oatmeal', 'type': 'product', 'calories': 68, 'protein': 2, 'fat': 1, 'carbs': 12},
    {'name': 'Banana', 'type': 'product', 'calories': 89, 'protein': 1, 'fat': 0, 'carbs': 23},
    {'name': 'Apple', 'type': 'product', 'calories': 52, 'protein': 0, 'fat': 0, 'carbs': 14},
    {'name': 'Broccoli', 'type': 'product', 'calories': 34, 'protein': 3, 'fat': 0, 'carbs': 7},
    {'name': 'Pasta', 'type': 'product', 'calories': 131, 'protein': 5, 'fat': 1, 'carbs': 25},
    {'name': 'Bread', 'type': 'product', 'calories': 265, 'protein': 9, 'fat': 3, 'carbs': 49},
    {'name': 'Milk', 'type': 'product', 'calories': 42, 'protein': 3, 'fat': 1, 'carbs': 5},
    {'name': 'Cheese', 'type': 'product', 'calories': 402, 'protein': 25, 'fat': 33, 'carbs': 1},
    {'name': 'Caesar Salad', 'type': 'dish', 'calories': 190, 'protein': 8, 'fat': 12, 'carbs': 12},
    {'name': 'Pasta Bolognese', 'type': 'dish', 'calories': 380, 'protein': 18, 'fat': 14, 'carbs': 45},
    {'name': 'Grilled Chicken Salad', 'type': 'dish', 'calories': 280, 'protein': 30, 'fat': 10, 'carbs': 15},
    {'name': 'Vegetable Soup', 'type': 'dish', 'calories': 75, 'protein': 3, 'fat': 1, 'carbs': 14},
    {'name': 'Steak with Vegetables', 'type': 'dish', 'calories': 450, 'protein': 40, 'fat': 25, 'carbs': 15},
]
