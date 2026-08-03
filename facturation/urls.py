from django.urls import path
from . import views

urlpatterns = [
    path("facturation/", views.CoutGlobalView.as_view(), name="cout_global"),
    path("facturation/<int:pk>/", views.CoutAppareilView.as_view(), name="cout_appareil"),
]