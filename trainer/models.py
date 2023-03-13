from django.core.exceptions import ValidationError
from django.db import models
from conf import settings


class Client(models.Model):
    first_name = models.CharField(max_length=10, blank=False)
    last_name = models.CharField(max_length=10, blank=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ClientTrainerRelationship(models.Model):
    STATUS_CHOICES = [
        ("ACT", "Active"),
        ("IA", "Inactive")
    ]
    RELATIONSHIP_CHOICES = [
        ("GLD", "Gold"),
        ("SLV", "Silver"),
        ("BRZ", "Bronze")
    ]
    date_joined = models.DateTimeField(auto_now_add=True)
    total_paid = models.DecimalField(decimal_places=2, max_digits=10, blank=False, null=False, default=0.00)
    status = models.CharField(choices=STATUS_CHOICES, max_length=3, blank=False, default="ACT")
    relationship_level = models.CharField(choices=RELATIONSHIP_CHOICES, max_length=3, blank=False, null=False,
                                          default="BRZ")
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                limit_choices_to={
                                    "groups__name": "Trainer"
                                }, blank=True, null=True)
    client = models.OneToOneField(Client, on_delete=models.SET_NULL, null=True, blank=True)


class TrainerSession(models.Model):
    TRAINING_TYPE = [
        ("GRP", "Group Personal Training"),
        ("SOLO", "Solo Personal Training")
    ]
    session_type = models.CharField(choices=TRAINING_TYPE, max_length=4, blank=False, null=False)
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                limit_choices_to={
                                    "groups__name": "Trainer"
                                })
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    sessions_left = models.PositiveIntegerField(default=8)


    def __str__(self):
        return f"PT session with {self.trainer} and {self.client}"

    def clean(self):
        try:
            relationship = ClientTrainerRelationship.objects.get(trainer=self.trainer, client=self.client)
        except ClientTrainerRelationship.DoesNotExist:
            raise ValidationError("There is no existing relationship between this client and this trainer. "
                                  "So, you cannot create a session between them.")


class SessionExerciseItem(models.Model):
    exercise_name = models.CharField(max_length=128, blank=True, null=True)
    sets = models.PositiveIntegerField(blank=False, null=False)
    reps = models.PositiveIntegerField(blank=False, null=False)


class SessionExercises(models.Model):
    exercises = models.ManyToManyField(SessionExerciseItem, blank=True)


class GroupClass(models.Model):
    class_name = models.CharField(max_length=100, blank=False)
    description = models.TextField(max_length=1000, blank=True)
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                limit_choices_to={
                                    "groups__name": "Trainer"
                                })

    def __str__(self):
        return self.class_name
