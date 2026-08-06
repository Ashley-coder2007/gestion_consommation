from django.urls import path
from . import views
from .api_views import ConsommationListCreateAPIView

urlpatterns = [
    path("consommation/", views.ConsommationGlobaleView.as_view(), name="consommation_globale"),
    path("consommation/<int:pk>/", views.ConsommationAppareilView.as_view(), name="consommation_appareil"),
    path("api/mesures/", ConsommationListCreateAPIView.as_view(), name="api_mesure_list_create")
]