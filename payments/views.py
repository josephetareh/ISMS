from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.paginator import Paginator
from django.shortcuts import render


# Create your views here.
from conf import constants
from conf.helper_functions import paginator_helper
from conf.url_tests import executive_test
from payments.models import PaySlip


@login_required()
def my_earnings(request):
    all_payslips = PaySlip.objects.filter(
        staff=request.user
    ).order_by("final_payment")
    total_payslips = all_payslips.count()
    total_payment = 0.00
    for payslip in all_payslips:
        total_payment += float(payslip.final_payment)

    page_object = paginator_helper(request, all_payslips, 10)
    context = {
        "total_payslips_count": total_payslips,
        "total_payment": total_payment,
        "first_payment": all_payslips.first(),
        "last_payment": all_payslips.last(),
        "page_object": page_object,
    }
    return render(request, "my-earnings.html", context)


@login_required()
def payslip_breakdown(request, payslip_identification):
    payslip = PaySlip.objects.get(
        id=int(payslip_identification),
        staff=request.user
    )
    is_trainer = constants.STAFF_MODEL.objects.filter(
        groups__name="Trainer",
        id=request.user.id
    ).exists()
    print(is_trainer)
    context = {
        "payslip": payslip,
        "is_trainer": is_trainer,
    }
    return render(request, "payslip-breakdown.html", context)