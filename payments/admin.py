from django.contrib import admin

# Register your models here.
from payments.models import PaySlip


@admin.register(PaySlip)
class PaySlipAdmin(admin.ModelAdmin):
    list_display = ("id", "paid", )