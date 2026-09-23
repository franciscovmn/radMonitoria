from django.urls import path

from . import views

app_name = "duvidas"

urlpatterns = [
    path("", views.DuvidaListView.as_view(), name="lista"),
    path("duvidas/<int:pk>/assumir/", views.assumir_duvida, name="assumir"),
    path("duvidas/<int:pk>/", views.DuvidaDetailView.as_view(), name="detalhe"),
    path("duvidas/nova/", views.DuvidaCreateView.as_view(), name="nova"),
]
