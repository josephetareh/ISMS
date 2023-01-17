from django.contrib.auth import get_user_model
from django.test import TestCase


# Create your tests here.
class UserManagersTests(TestCase):

    def test_create_user(self):
        user = get_user_model()
        user = user.objects.create_user(email="normal@user.com", username="normal", password="foo")
        self.assertEqual(user.email, "normal@user.com")
        self.assertEqual(user.username, "normal")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_create_user_no_username(self):
        user = get_user_model()
        with self.assertRaises(TypeError):
            user.objects.create_user(email="normal@user.com", password="foo")
        with self.assertRaises(TypeError):
            user.objects.create_user(username="nm@user.com", password="foo")
        with self.assertRaises(ValueError):
            user.objects.create_user(username="nm", email="", password="foo")


class TestLogin(TestCase):

    def test_staff_login(self):
        pass
