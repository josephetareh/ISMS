from django.db.models import Prefetch
from django.shortcuts import render

# Create your views here.
from tasks.models import Task, SubTask, SubTaskDependency


def my_tasks(request):
    # filter through tasks to display all the tasks
    tasks_working_on = Task.objects.filter(working_on=request.user)
    task_dictionary = {}

    task_subtasks = SubTask.objects.filter(task__in=tasks_working_on, assigned_to=request.user)
    dependencies = SubTaskDependency.objects.filter(from_subtask__in=task_subtasks).values_list('from_subtask',
                                                                                                'dependency_status')


    context = {
        "user_tasks": task_dictionary
    }
    return render(request, 'my-tasks.html', context)


def task_detail(request):
    # get task detail
    pass
