from django.urls import path

from tasks import views

app_name = 'tasks'

urlpatterns = [
    path('my-tasks/', views.my_tasks, name="my-tasks"),
]