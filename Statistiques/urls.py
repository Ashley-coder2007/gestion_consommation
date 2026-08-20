from django.urls import path
from . import views
from .api_views import StatistiqueListCreateAPIView

urlpatterns = [
    path('statistiques/', views.StatistiqueView.as_view(), name='statistique'),
    path("api/statistiques/", StatistiqueListCreateAPIView.as_view(), name="api_statistique_list"),
    path('', views.StatistiqueView.as_view(), name='statistiques'),
    path('lancer-nilm/', views.lancer_nilm_demo, name='lancer_nilm_demo')
]