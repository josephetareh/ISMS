from django.conf import settings
from django.db import models

# Create your models here.
STATUS_CHOICES = [
    ("FR", "Fresh Tasks"),
    ("IPR", "In Progress Tasks"),
    ("ESC", "Escalated Tasks"),
    ("COMP", "Complete Tasks"),
    ("ARCH", "Archived Tasks"),
]

PRIORITY_CHOICES = [
    ("0", "Low"),
    ("1", "Medium"),
    ("3", "High"),
]


class Task(models.Model):
    task_name = models.CharField(max_length=128)
    start_date = models.DateTimeField(null=True, blank=True)
    deadline_date = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    system_task = models.BooleanField(default=False)
    status = models.CharField(choices=STATUS_CHOICES, max_length=4)
    priority = models.CharField(blank=True, null=True, choices=PRIORITY_CHOICES, max_length=1)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name="task_creator")
    working_on = models.ManyToManyField(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="working_on")
    last_modified = models.DateTimeField(auto_now=True)
    description = models.TextField()

    def __str__(self):
        return self.task_name


class SubTask(models.Model):
    SUBTASK_TYPE_CHOICES = [
        ("FTSK", "Form Task"),
        ("UTSK", "Upload Task"),
        ("GTSK", "Generic Task"),
    ]
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="subtask_parent")
    subtask_name = models.CharField(max_length=128)
    status = models.CharField(choices=STATUS_CHOICES, max_length=4)
    dependencies = models.ManyToManyField('self', through='SubTaskDependency',
                                          symmetrical=False, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    description = models.TextField()
    subtask_type = models.CharField(max_length=4, choices=SUBTASK_TYPE_CHOICES, default="GTSK")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    subtask_order = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.subtask_name

    def save(self, *args, **kwargs):
        working_task = Task.objects.get(id=self.task.id)
        working_task.working_on.add(self.assigned_to)
        working_task.save()
        super().save(*args, **kwargs)


class Question(models.Model):
    subtask = models.ForeignKey(SubTask, on_delete=models.CASCADE, null=True)
    question_text = models.TextField()


class SubTaskDependency(models.Model):
    DEPENDENCY_CHOICES = [
        ("BLK", "Blocking"),
        ("WTN", "Waiting")
    ]
    from_subtask = models.ForeignKey(SubTask, on_delete=models.CASCADE, related_name="from_subtask")
    to_subtask = models.ForeignKey(SubTask, on_delete=models.CASCADE, related_name="to_subtask")
    dependency_status = models.CharField(max_length=3, choices=DEPENDENCY_CHOICES, default="BLK")

    class Meta:
        # this will ensure that a dependency from_subtask cannot be created for the same  to_subtask
        # if it already exists
        constraints = [
            models.UniqueConstraint(fields=['from_subtask', 'to_subtask'], name='unique_subtask_dependency')
        ]
