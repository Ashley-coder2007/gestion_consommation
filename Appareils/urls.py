from django.urls import path
from . import views
from .api_views import AppareilListCreateAPIView, AppareilDetailAPIView

urlpatterns = [
    path("appareils/", views.AppareilListView.as_view(), name="appareil_list"),
    path("appareils/ajouter/", views.AppareilAjouterView.as_view(), name="appareil_ajouter"),
    path("appareils/<int:pk>/modifier/", views.AppareilModifierView.as_view(), name="appareil_modifier"),
    path("appareils/<int:pk>/supprimer/", views.appareil_supprimer, name="appareil_supprimer"),
    path("appareils/<int:pk>/toggle/", views.appareil_toggle, name="appareil_toggle"),

    path("api/appareils/", AppareilListCreateAPIView.as_view(), name="api_appareil_list"),
    path("api/appareils/<int:pk>/", AppareilDetailAPIView.as_view(), name="api_appareil_detail"),
]