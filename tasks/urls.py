from django.urls import path

from tasks import views

app_name = 'tasks'

urlpatterns = [
    path('', views.my_tasks, name="my-tasks"),
    path('detail/<task_id>/<slug>/', views.task_detail, name="task-detail"),
    path("subtask-detail/<subtask_id>/<slug>", views.subtask_detail, name="subtask-detail"),
]
