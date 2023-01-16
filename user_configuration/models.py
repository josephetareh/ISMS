from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from user_configuration.managers import CustomUserManager


class CustomUser(AbstractUser):
    username = models.CharField(max_length=128, unique=True)
    email = models.EmailField(unique=True)
    objects = CustomUserManager()

    # REQUIRED_FIELDS
    # TODO: IN THE FUTURE, WE WILL NEED TO SET SOME REQUIRED_FIELDS FOR CREATING SUPERUSER
    # https://docs.djangoproject.com/en/4.1/topics/auth/customizing/#specifying-custom-user-model

    def __str__(self):
        return self.username
