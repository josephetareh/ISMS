from django.urls import path

from executive import views

app_name = "executive"

urlpatterns = [
    path("staff-payments/", views.staff_payments, name="staff-payments"),

]