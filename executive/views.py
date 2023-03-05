from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render

# Create your views here.
from django.utils import timezone

from conf import constants
from conf.url_tests import executive_test
from payments.models import PaySlip


@user_passes_test(executive_test)
@login_required()
def staff_payments(request):
    # todo: post testing staff = constants.STAFF_MODEL.objects.all.exclude(groups__name__in=['Executive'])
    staff_to_pay = constants.STAFF_MODEL.objects.filter(
        groups__name__in=['Trainer', 'Front Desk']
    )
    payments_list = []
    for gym_staff in staff_to_pay:
        payments_slip = PaySlip.objects.filter(
            staff=gym_staff,
            paid=False,
        )
        if payments_slip.count() > 1:
            for payment in payments_slip:
                payments_list.append(payment)
        elif payments_slip.count() == 1:
            payments_list.append(payments_slip.first())

    if request.method == "POST" and request.POST.get("slip-id"):
        payslip = PaySlip.objects.get(
            id=int(request.POST.get("slip-id"))
        )
        payslip.payment_confirmed = timezone.now()
        payslip.paid = True
        payslip.save()
        return render(request, 'partials/staff-payments.html', {"payment": payslip})

    context = {
        "staff": staff_to_pay,
        "payments_list": payments_list,
    }
    return render(request, "staff-payments.html", context)
