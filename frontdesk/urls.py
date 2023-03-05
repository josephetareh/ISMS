from django.urls import path

from frontdesk import views

app_name = "frontdesk"

urlpatterns = [
    path("log-classes/", views.log_class_attendance, name="log-classes"),
    path("create-payslip/", views.create_payslip, name="create-payslip"),
]
