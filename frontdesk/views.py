from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db import transaction
from django.shortcuts import render

# Create your views here.
from django.utils import timezone

from conf import constants
from conf.url_tests import not_a_trainer_test, frontdesk_test
from payments.models import PaySlip, GroupClassPayment
from staff_schedule.models import ClockIn


@login_required()
@user_passes_test(frontdesk_test)
def log_class_attendance(request):
    # todo: auto task item
    unregistered_classes = GroupClassPayment.objects.filter(attendees=0, class_paid_for=False,
                                                            attendance_logged=False). \
        prefetch_related("payment_for_class", "payment_for_class__trainer"). \
        order_by("payment_request_created")
    if request.method == "POST":
        if request.POST.get("attendance-for"):
            group_class_payment_id = request.POST.get("attendance-for")
            group_class_payment = GroupClassPayment.objects.get(
                id=int(group_class_payment_id)
            )
            group_class_payment.attendees = request.POST.get(f"class-{group_class_payment_id}")
            group_class_payment.total_payment = group_class_payment.payment_for_class.trainer.payment_per_class
            group_class_payment.attendance_logged = True
            group_class_payment.save()
            return render(request, "partials/post-log-class-attendance.html",
                          {"unregistered_class": group_class_payment}
                          )
        else:
            messages.error(request,
                           "The attendance for this class could not be logged. Please refresh this page and try again.")

    context = {
        'unregistered_classes': unregistered_classes
    }
    return render(request, 'log-class-attendance.html', context)


@user_passes_test(frontdesk_test)
def create_payslip(request):
    # todo: make periodic task
    # step 1: filter for all unpaid classes:
    # step 2: filter for all unpaid classes where the invoice was created on or before the request
    # was made on or before the last saturday of the month
    # todo: add here that only staff that only active staff [staff that are currently working, should be paid
    # this will ensure that when they are deleted from the system and the payslip for their clock ins is once
    # again set to null they are not looked at by the system
    staff_to_create_payslips_for = constants.STAFF_MODEL.objects.filter(
        groups__name__in=["Trainer", "Front Desk"]
    )
    print(staff_to_create_payslips_for)
    current_day = timezone.now()
    with transaction.atomic():
        # # todo: change to objects.create after testing
        # payslip_added_to = PaySlip

        for staff in staff_to_create_payslips_for:
            print(f"for: {staff}")
            payslip_added_to = PaySlip.objects.create()
            unpaid_clock_ins_for_month = ClockIn.objects.filter(
                paid=False,
                time_clocked_in__lte=current_day,
                on_shift=True,
                shift__staff_on_shift=staff,
                payslip=None
            )
            total_deductions = float(0.00)
            total_clock_ins_payment = float(0.00)
            for clock_in in unpaid_clock_ins_for_month:
                clock_in.payslip = payslip_added_to
                total_clock_ins_payment += float(clock_in.payment_for_shift)
                if clock_in.deduction > 0:
                    total_deductions += float(clock_in.deduction)
                clock_in.save()
                payslip_added_to.total_clock_in_wage = float(total_clock_ins_payment)
                payslip_added_to.deductions = float(total_deductions)
                payslip_added_to.final_payment = float(total_clock_ins_payment - total_deductions)

            if staff.groups.filter(name="Trainer").exists():
                unpaid_group_classes_for_month = GroupClassPayment.objects.filter(
                    attendees__gte=1,
                    class_paid_for=False,
                    sent_for_payment=True,
                    payment_request_created__lte=current_day,
                    payment_for_class__trainer=staff,
                    payslip=None
                )
                class_payment = float(0.00)
                for group_class in unpaid_group_classes_for_month:
                    group_class.payslip = payslip_added_to
                    class_payment += float(group_class.total_payment)
                    group_class.save()
                payslip_added_to.total_class_payment = class_payment
                payslip_added_to.final_payment += float(class_payment)
                # todo: add for home and add for classes
            # delete model instance if there was nothing to add to it:
            if payslip_added_to.final_payment == 0:
                payslip_added_to.delete()
            else:
                payslip_added_to.payslip_type = "GNL"
                payslip_added_to.staff = staff
                payslip_added_to.save()

    return render(request, "create-payslip.html")
