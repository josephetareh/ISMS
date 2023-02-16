from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django_json_widget.widgets import JSONEditorWidget

from user_configuration.models import CustomUser


class CustomUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = CustomUser
        fields = ('email', 'basic_hourly_wage', 'preferences')

        widgets = {
            'preferences': JSONEditorWidget
        }


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'basic_hourly_wage', 'preferences')

        widgets = {
            'preferences': JSONEditorWidget
        }


class UserLoginForm(forms.Form):
    email_or_pass = forms.CharField(label="Email or Username", help_text="Input Your Email or Username")
    password = forms.CharField(widget=forms.PasswordInput())
