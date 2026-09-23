from django.urls import path

from . import views

app_name = "duvidas"

urlpatterns = [
    path("", views.DuvidaListView.as_view(), name="lista"),
    path("base-conhecimento/", views.BaseConhecimentoListView.as_view(), name="base_conhecimento"),
    path("duvidas/<int:pk>/encerrar/", views.encerrar_duvida, name="encerrar"),
    path("duvidas/<int:pk>/responder/", views.responder_duvida, name="responder"),
    path("duvidas/<int:pk>/assumir/", views.assumir_duvida, name="assumir"),
    path("duvidas/<int:pk>/", views.DuvidaDetailView.as_view(), name="detalhe"),
    path("duvidas/nova/", views.DuvidaCreateView.as_view(), name="nova"),
]
