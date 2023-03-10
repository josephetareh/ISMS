from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from user_configuration.forms import CustomUserCreationForm, CustomUserChangeForm
from user_configuration.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("username", "email", "is_staff", "is_active",)
    list_filter = ("username", "email", "is_staff", "is_active")
    fieldsets = (
        (None, {'fields': ('username', 'email', 'first_name', 'last_name', 'basic_hourly_wage', 'payment_per_class',
                           'preferences', 'password', 'groups')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'basic_hourly_wage', 'first_name', 'last_name', 'preferences',
                       'payment_per_class',
                       'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)