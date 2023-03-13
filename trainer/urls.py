from django.urls import path

from trainer import views

app_name = "trainer"

urlpatterns = [
    path("my-clients/", views.my_clients, name="my-clients"),
    path("my-sessions/<int:calendar_event_identification>/<slug_details>/", views.my_sessions, name="my-sessions"),
    path("add-exercise/<int:calendar_event_identification>/<slug_details>/", views.add_exercise, name="add-exercise"),
]