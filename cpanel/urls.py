from . import views
from django.urls import path


urlpatterns = [
    path("dashboard", views.cpanel, name="cpanel"),
    path("start", views.start, name="start"),
    path("fetchlogs", views.fetchlogs, name="fetchlogs"),
    path("showlogs", views.showlogs, name="showlogs"),
    path("clearlogs", views.clearlogs, name="clearlogs"),
]
