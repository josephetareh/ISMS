from django.db.models import Prefetch
from django.shortcuts import render

# Create your views here.
from tasks.models import Task, SubTask, SubTaskDependency


def my_tasks(request):
    # filter through tasks to display all the tasks

    # this will be the conditional if the subtasks are not being shown —
    # by default, they will not be shown on the main page:

    user_tasks = Task.objects.filter(working_on=request.user)
    task_dictionary = {}
    related_subtasks = SubTask.objects.filter(task__in=user_tasks, assigned_to=request.user).\
        prefetch_related('dependencies', "task")
    for count, item in enumerate(related_subtasks):
        print(item.task.task_name)
        print(item.subtask_name)
        dependencies = SubTaskDependency.objects.filter(from_subtask=item)\
            .select_related('to_subtask', 'from_subtask').values_list('to_subtask', 'dependency_status')
        task_dictionary[count] = [item.task.task_name, item.subtask_name, dependencies]

    print(task_dictionary)

    # for task in user_tasks:
    #     print(task.subtask_parent.all())
    #     subtasks_dependencies = SubTask.objects.filter(task__in=task)prefetch_related('dependencies')

    # context = {
    #     "user_tasks": task_dictionary,
    # }
    return render(request, 'my-tasks.html')


def task_detail(request):
    # get task detail
    pass
