from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from Accueil.views import AccueilView

urlpatterns = [
    path('', AccueilView.as_view(), name='accueil'),
    path('admin/', admin.site.urls),
    path('', include('Appareils.urls')),
    path('', include('Consommation.urls')),
    path('', include('facturation.urls')),
    path('', include('Statistiques.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]