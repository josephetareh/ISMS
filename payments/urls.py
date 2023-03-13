from django.urls import path

from payments import views

app_name = "payments"

urlpatterns = [
    path("my-earnings/", views.my_earnings, name="my-earnings"),
    path("payslip-breakdown/<int:payslip_identification>/", views.payslip_breakdown, name="payslip-breakdown"),
]