from django.urls import path

from . import views

app_name = "duvidas"

urlpatterns = [
    path("duvidas/nova/", views.DuvidaCreateView.as_view(), name="nova"),
]
