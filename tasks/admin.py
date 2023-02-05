from django.contrib import admin

# Register your models here.
from tasks.models import SubTask, Task, SubTaskDependency


class SubtaskInline(admin.TabularInline):
    model = SubTask
    show_change_link = True


class DependenciesInline(admin.TabularInline):
    fk_name = "from_subtask"
    model = SubTaskDependency


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("task_name", "start_date", "deadline_date")
    inlines = [SubtaskInline]


@admin.register(SubTask)
class SubtaskAdmin(admin.ModelAdmin):
    list_display = ("task", "subtask_name", "last_modified")
    inlines = [DependenciesInline]


@admin.register(SubTaskDependency)
class SubTaskDependencyAdmin(admin.ModelAdmin):
    list_display = ("from_subtask", "to_subtask", "dependency_status")