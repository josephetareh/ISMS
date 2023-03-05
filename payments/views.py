from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render


# Create your views here.
from conf.url_tests import executive_test
from payments.models import PaySlip


@login_required()
def my_earnings(request):
    all_payslips = PaySlip.objects.filter(
        staff=request.user
    )
    total_payslips = all_payslips.count()
    total_payment = 0.00
    for payslip in all_payslips:
        total_payment += float(payslip.final_payment)
    context = {
        "total_payslips_count": total_payslips,
        "total_payment": total_payment,
        "payslips": all_payslips,
        "first_payment": all_payslips.first(),
        "last_payment": all_payslips.last(),
    }
    return render(request, "my-earnings.html", context)