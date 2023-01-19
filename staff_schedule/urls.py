from django.urls import path

from staff_schedule import views

app_name = "schedule"

urlpatterns = [
    path("", views.personal_schedule, name="personal-schedule"),
    path('<schedule_date>/', views.personal_schedule, name="personal-schedule"),
    path('<schedule_date>/<activity>', views.personal_schedule, name="personal-schedule"),
]