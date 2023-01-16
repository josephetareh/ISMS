from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):

    def create_user(self, username, email, password, **extra_fields):
        """
        method creates and saves the given CustomUser with the given email, username, and password
        :param username: the provided username of the user
        :param email: the provided email of the user
        :param password: the provided password of the user
        :param extra_fields: any extra fields that will be added to the CustomUser model
        :return: the CustomUser object
        """

        # ensure that both the emails and passwords have been provided
        if not email:
            raise ValueError("You Must Provide an Email to Register")
        if not username:
            raise ValueError("You Must Provide a Username to Register")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        """
        method creates and saves the given CustomUser as a superuser with the given email, username, and password
        :param username: the provided username of the user
        :param email: the provided email of the user
        :param password: the provided password of the user
        :param extra_fields: any extra fields that will be added to the CustomUser model
        :return: the CustomUser object
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(username, email, password, **extra_fields)
