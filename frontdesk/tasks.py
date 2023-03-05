from celery import shared_task
from django.db import transaction
from django.utils import timezone

from conf import constants
from payments.models import PaySlip
from staff_schedule.models import ClockIn


@shared_task
def create_payslips():
    """
    this task will run on the 30th day of each month
    :return: None
    """
    # get all the staff
    # todo: finish naming here for all groups
    staff_to_create_payslips_for = constants.STAFF_MODEL.groups.filter(
        name_in=["Front Desk", "Trainer"]
    )
    current_day = timezone.now()
    with transaction.atomic():
        payslip_added_to = PaySlip.objects.create(
        )
        for staff in staff_to_create_payslips_for:
            unpaid_clock_ins_for_month = ClockIn.objects.filter(
                paid=False,
                time_clocked_in__month=current_day.month,
                time_clocked_in__day__lte=current_day.day,
                time_clocked_in__year=current_day.year,
                on_shift=True,
                shift__staff_on_shift=staff
            )
            for clock_in in unpaid_clock_ins_for_month:
                clock_in.payslip = payslip_added_to
