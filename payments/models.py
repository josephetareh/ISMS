from django.conf import settings
from django.db import models


# Create your models here.
class PaySlip(models.Model):
    paid = models.BooleanField(default=False)
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    deductions = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    total_clock_in_wage = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    total_class_payment = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    final_payment = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    payment_confirmed = models.DateTimeField(blank=True, null=True)
