from django.conf import settings
from django.db import models


# Create your models here.
from trainer.models import GroupClass


class PaySlip(models.Model):
    PAYSLIP_TYPES = [
        ("GNL", "General"),
        ("OOO", "One-on-One")
    ]
    paid = models.BooleanField(default=False)
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    deductions = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    total_clock_in_wage = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    total_class_payment = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    final_payment = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    payment_confirmed = models.DateTimeField(blank=True, null=True)
    payslip_type = models.CharField(choices=PAYSLIP_TYPES, default="GNL", blank=False, max_length=3)


class GroupClassPayment(models.Model):
    payment_for_class = models.ForeignKey(GroupClass, on_delete=models.SET_NULL, null=True, blank=True)
    attendees = models.PositiveIntegerField(default=0, blank=True, null=True)
    attendance_logged = models.BooleanField(default=False)
    payment_request_created = models.DateTimeField(auto_now_add=True)
    time_of_payment = models.DateTimeField(null=True, blank=True)
    class_paid_for = models.BooleanField(default=False)
    total_payment = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    sent_for_payment = models.BooleanField(default=False)
    payslip = models.ForeignKey(PaySlip, null=True, blank=True, on_delete=models.SET_NULL)
