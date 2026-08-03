from django.urls import path
from . import views

urlpatterns = [
    path('statistiques/', views.StatistiqueView.as_view(), name='statistique'),
]