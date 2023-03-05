from django.urls import path

from payments import views

app_name = "payments"

urlpatterns = [
    path("my-earnings/", views.my_earnings, name="my-earnings"),
]