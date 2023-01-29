from django.urls import path

from staff_schedule import views

app_name = "schedule"

urlpatterns = [
    path("", views.personal_schedule, name="personal-schedule"),
    path('<schedule_weekday>/', views.personal_schedule, name="personal-schedule"),
    path('<schedule_weekday>/<activity>', views.personal_schedule, name="personal-schedule"),
    path("clock-in", views.clock_in, name="clock-in")
]