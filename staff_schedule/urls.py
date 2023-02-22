from django.urls import path

from staff_schedule import views

app_name = "schedule"

urlpatterns = [
    path("", views.personal_schedule, name="personal-schedule"),
    path("clock-in", views.clock_in, name="clock-in"),
    path("log-clock-in/<clock_in_id>/", views.log_clock_in, name="log-clock-in"),
    path('month-clock-ins/<month_query>/<year_query>/',
         views.clock_ins_for_current_month, name='month-clock-ins'),
    path("clock-in-insights/<clock_in_id>/", views.clock_in_insights, name="clock-in-insights"),
    path("dispute-clock-ins/", views.dispute_clock_in, name="dispute-clock-ins"),
    path("log-dispute/<clock_in_id>", views.log_dispute, name="log-dispute"),
    path("all-clock-ins", views.total_clock_ins, name="total-clock-ins"),
    # path('<schedule_weekday>/', views.personal_schedule, name="personal-schedule"),
    # path('<schedule_weekday>/<activity>', views.personal_schedule, name="personal-schedule"),

]