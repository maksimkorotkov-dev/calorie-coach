from django.urls import path
from . import views

urlpatterns = [
    path('', views.calculator, name='calculator'),
    path('diary/', views.diary, name='diary'),
    path('add-food/', views.add_food, name='add_food'),
    path('add-custom-food/', views.add_custom_food, name='add_custom_food'),
    path('delete-food/<int:food_id>/', views.delete_food, name='delete_food'),
    path('add-activity/', views.add_activity, name='add_activity'),
    path('delete-activity/<int:activity_id>/', views.delete_activity, name='delete_activity'),
]
