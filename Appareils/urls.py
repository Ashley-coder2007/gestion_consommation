from django.urls import path
from . import views

urlpatterns = [
    path("appareils/", views.AppareilListView.as_view(), name="appareil_list"),
    path("appareils/ajouter/", views.AppareilAjouterView.as_view(), name="appareil_ajouter"),
    path("appareils/<int:pk>/modifier/", views.AppareilModifierView.as_view(), name="appareil_modifier"),
    path("appareils/<int:pk>/supprimer/", views.appareil_supprimer, name="appareil_supprimer"),
    path("appareils/<int:pk>/toggle/", views.appareil_toggle, name="appareil_toggle"),
]