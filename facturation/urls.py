from django.urls import path
from . import views
from .api_views import TarifListCreateAPIView, FactureListCreateAPIView

urlpatterns = [
    path("facturation/", views.CoutGlobalView.as_view(), name="cout_global"),
    path("facturation/<int:pk>/", views.CoutAppareilView.as_view(), name="cout_appareil"),
    path("api/tarifs/", TarifListCreateAPIView.as_view(), name="api_tarif_list"),
    path("api/factures/", FactureListCreateAPIView.as_view(), name="api_facture_list"),
]