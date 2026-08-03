from django.urls import path
from . import views

urlpatterns = [
    path("consommation/", views.ConsommationGlobaleView.as_view(), name="consommation_globale"),
    path("consommation/<int:pk>/", views.ConsommationAppareilView.as_view(), name="consommation_appareil"),
]