from django.db.models import Prefetch
from django.shortcuts import render

# Create your views here.
from tasks.models import Task, SubTask, SubTaskDependency


def my_tasks(request):
    # filter through tasks to display all the tasks

    # this will be the conditional if the subtasks are not being shown —
    # by default, they will not be shown on the main page:
    # user_subtasks = SubTask.objects.filter(assigned_to=request.user).select_related('task')
    user_tasks = Task.objects.filter(working_on=request.user).prefetch_related('subtask_parent',
                                                                               'subtask_parent__dependencies')
    task_dictionary = {}
    for task in user_tasks:
        subtasks = task.subtask_parent.all()
        task_dictionary[task] = subtasks
    context = {
        "task_items": task_dictionary
    }

    return render(request, 'my-tasks.html', context)


def task_detail(request, slug, task_id):
    current_task = Task.objects.get(id=task_id, slug=slug)
    subtasks = SubTask.objects.filter(task=current_task, assigned_to=request.user)
    context = {
        "current_task": current_task,
        "subtasks": subtasks
    }
    return render(request, "task-detail.html", context)


def subtask_detail(request, slug, subtask_id):
    pass
