from django.contrib.auth.views import LogoutView
from django.urls import path

from user_configuration import views

app_name = 'user_configuration'

urlpatterns = [
    path('login/', views.staff_login, name="staff-login"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('logout/', LogoutView.as_view(next_page='user_configuration:staff-login'), name="logout"),
]