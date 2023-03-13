import datetime
import calendar
from collections import deque
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.db import transaction
from django.db.models import Count, Q
from django.forms import modelform_factory, modelformset_factory
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from environ import environ
from haversine import haversine, Unit

from conf.helper_functions import paginator_helper
from conf.url_tests import not_a_trainer_test, trainer_test
from payments.models import GroupClassPayment
from staff_schedule.forms import DisputeForm, DisputeAttachmentForm
from staff_schedule.models import Shift, ClockIn, Dispute, DisputeAttachment, ISMSScheduleFixedEvent, \
    ISMSScheduleCalendarEvent

env = environ.Env()


@login_required()
def personal_schedule(request):
    context = {}
    if request.GET:
        activity_type = request.GET.get("activity")
        schedule_weekday = request.GET.get("weekday")  # int value

        schedule_weekday = timezone.now().weekday() if schedule_weekday is None else int(schedule_weekday)
        context['schedule_weekday'] = schedule_weekday
        context['schedule_weekday_string'] = calendar.day_name[context['schedule_weekday']]

        if activity_type is None or activity_type == "ALL":
            activities = ISMSScheduleFixedEvent.objects.filter(
                Q(group_class__trainer=request.user) | Q(staff_meeting__staff_attending=request.user),
                schedule_day=schedule_weekday,
            ).select_related('staff_meeting', 'group_class').order_by("start_time")
            activity_type = "ALL"
        else:
            activities = ISMSScheduleFixedEvent.objects.filter(
                Q(group_class__trainer=request.user) | Q(staff_meeting__staff_attending=request.user),
                schedule_day=schedule_weekday, schedule_type=activity_type
            ).select_related('staff_meeting', 'group_class').order_by("start_time")
        context['activity_type'] = activity_type
        context['activities'] = activities
    else:
        schedule_weekday = timezone.now().weekday()
        activities = ISMSScheduleFixedEvent.objects.filter(
            Q(group_class__trainer=request.user) | Q(staff_meeting__staff_attending=request.user),
            schedule_day=schedule_weekday,
        ).select_related('staff_meeting', 'group_class').order_by("start_time")
        context['activity_type'] = "ALL"
        context['activities'] = activities
        context['schedule_weekday'] = schedule_weekday
        context['schedule_weekday_string'] = calendar.day_name[context['schedule_weekday']]

    date_shifter = deque([0, 1, 2, 3, 4, 5, 6])
    # rotate function here to always ensure that the first date on our deque is the current weekday
    date_shifter.rotate(0 - schedule_weekday)

    context['deque_of_days'] = date_shifter
    context['previous_day'] = date_shifter[6]
    context['next_day'] = date_shifter[1]
    return render(request, "personal-schedule.html", context)


@login_required()
@user_passes_test(trainer_test)
def class_details(request, class_name, class_identification, slug):
    """
    :param request:
    :param class_name: the name of the class automatically generated in the URL but not used
    :param class_identification:  the id of the class
    :param slug: the aut-generated slug
    :return: django request object
    this view works by getting the requested class from the ISMS schedule table. one it has the class it then
    attempts to determine if a payment request for the class in question has already been created. in order
    to reduce the amount of data in the database tables, the schedule has been created programmatically,
    which also means that this problem also has to be solved programmatically. unfortunately, the obvious
    limitation at this time of writing is that class payment requests will only be able to crated on the day of
    the class and after the class has ended.

    the first core task that this view solves is that it tries to check if a payment request for a class has
    already been created. as classes are a FK on the GroupClassPayment schedule, it attempts to use
    the date to check if a GroupClassPayment has been made for a specific class has been made by a specific
    trainer. this hereby works on the context that a trainer will never handle the same class twice in one day
    i.e., a trainer will never take two HIITs classes in the same day.

    if no GroupClassPayment object exists, then it is sets it to none, and then it checks if the current class that
    is being viewed is being viewed on the same weekday is the same as the current time, and then checks if
    the current time has passed the time that is being viewed is >= the class end time [this is to ensure that a
    trainer will only ever be able to request a payment for a class until after its designated end time and not before]

    the last core functionality is that if the system is able to find a GroupClassPayment for a specific class,
    made on the same day, by the current trainer, then we can make a .99 assumption that the trainer has already
    requested a payment in the past. so it sends a message to the trainer that a payment has already been made
    for that class has been made, and then tells that if they did not perform this action, they should visit the front
    desk.

    while this is not necessarily a fool-proof implementation, I believe it is much better than the infinite amount of
    database rows that would have to be created for each single class that is had on the gym. so, it is a positive tradeoff
    """
    class_viewing = ISMSScheduleFixedEvent.objects.get(
        slug=slug,
        id=int(class_identification),
        group_class__trainer=request.user
    )
    context = {}
    current_time = timezone.now()
    can_end_class = False

    try:
        payment_request_for_class = GroupClassPayment.objects.get(
            payment_for_class=class_viewing.group_class,
            payment_for_class__trainer=request.user,
            payment_request_created__day=current_time.day,
            payment_request_created__month=current_time.month,
            payment_request_created__year=current_time.year
        )
    except GroupClassPayment.DoesNotExist:
        payment_request_for_class = None

    if payment_request_for_class is None:
        if class_viewing.end_time.weekday() == current_time.weekday() \
                and current_time.hour >= class_viewing.end_time.hour \
                and current_time.minute >= class_viewing.end_time.minute:
            can_end_class = True

        if request.method == "POST" and request.POST.get('request-payment'):
            GroupClassPayment.objects.create(
                payment_for_class=class_viewing.group_class,
                sent_for_payment=True
            )
            messages.success(
                request,
                "Your payment request has been created. It will now be added to your next invoice"
            )
            can_end_class = False
    else:
        if class_viewing.end_time.weekday() == payment_request_for_class.payment_request_created.weekday():
            messages.warning(
                request,
                "A payment for this class has already been made today. "
                "This means that you cannot request a payment for this class until the next time "
                "it appears on your schedule. Please visit the front desk if you believe that this "
                "is an error."
            )

    context['class_details'] = class_viewing
    context['can_end_class'] = can_end_class
    return render(request, "class-details.html", context)


@login_required()
def my_calendar(request):
    context = {}
    if not request.GET:
        current_day = timezone.now()
        list_of_events = ISMSScheduleCalendarEvent.objects.filter(
            Q(meeting_event__staff_attending=request.user) | Q(personal_training_event__trainer=request.user),
            start_date__day=current_day.day
        ).distinct().order_by("start_date").prefetch_related("personal_training_event__client")

        context['calendar_events'] = list_of_events
        context['date_viewing'] = current_day, current_day.strftime("%V")
    else:
        day, month, year = int(request.GET.get("day")), int(request.GET.get("month")), int(request.GET.get("year"))
        list_of_events = ISMSScheduleCalendarEvent.objects.filter(
            Q(meeting_event__staff_attending=request.user) | Q(personal_training_event__trainer=request.user),
            start_date__day=day,
            start_date__month=month,
            start_date__year=year,
        ).distinct().order_by("start_date").prefetch_related("personal_training_event__client")
        context['calendar_events'] = list_of_events
        new_date = timezone.now().replace(year=year, month=month, day=day)
        context['date_viewing'] = new_date, new_date.strftime("%V")
    return render(request, "my-calendar.html", context)


@login_required()
def update_shifts():
    # todo: add role requirements to this
    pass


@login_required()
def clock_in(request):
    """
    this view allows all staff to register a clock in for their service.
    it works by
    :param request:
    :return:
    """

    context = {}
    current_time = timezone.now()
    current_month = current_time.month
    clock_ins_this_month = ClockIn.objects.filter(
        time_clocked_in__month=current_month, shift__staff_on_shift=request.user
    )
    all_clock_ins = ClockIn.objects.filter(shift__staff_on_shift=request.user,
                                           time_clocked_in__isnull=False)
    context['month_clock_ins'] = clock_ins_this_month
    context['all_clock_ins'] = all_clock_ins

    # early and late clock in count:
    late_clock_ins = all_clock_ins.filter(status="LTE").count()
    context['late_clock_ins'] = late_clock_ins if late_clock_ins > 0 else 0
    early_clock_ins = all_clock_ins.filter(status="EA").count()
    context['early_clock_ins'] = early_clock_ins if early_clock_ins > 0 else 0

    # dispute count:
    pending_disputes = all_clock_ins.filter(status="DSP").count()
    context['pending_disputes'] = pending_disputes if pending_disputes > 0 else 0
    successful_disputes = all_clock_ins.filter(status="DSPS").count()
    context['successful_disputes'] = successful_disputes if successful_disputes > 0 else 0
    unsuccessful_disputes = all_clock_ins.filter(status="DSPF").count()
    context['unsuccessful_disputes'] = unsuccessful_disputes if unsuccessful_disputes > 0 else 0
    all_disputes = unsuccessful_disputes + successful_disputes + pending_disputes
    context['all_disputes'] = all_disputes

    next_clock_ins_registered = \
        ClockIn.objects.filter(shift__staff_on_shift=request.user, shift_ends__gte=timezone.now()
                               ).select_related('shift').order_by('shift_starts')[:7]
    next_clock_in = next_clock_ins_registered.first()
    context["registered_clock_ins"] = next_clock_ins_registered

    if next_clock_in:
        time_to_open = next_clock_in.shift_starts - datetime.timedelta(minutes=40)
        context['active_clock_in'] = next_clock_in
        context['time_to_open'] = time_to_open.isoformat()
        context['iso_shift_starting_time'] = next_clock_in.shift_starts.isoformat()
        context['iso_shift_ending_time'] = next_clock_in.shift_ends.isoformat()
    else:
        context['time_to_open'] = ""
        context['active_clock_in'] = None
    context['current_time'] = current_time
    return render(request, 'clock-in.html', context)


def log_clock_in(request, clock_in_id):
    """
    this view is used to log any fresh clock in. it firstly does so by checking that the user is always within 500
     meters of the gym location. if the user is not within the specified location, then they are not to be allowed
     to be clocked in.

     this view requires a number of variables to ensure that the data is manipulated properly:
     - deduction_block: this variable calculates the difference between the current time and the time that deductions
            begin. so, if a shift begins at 10:00, and the current time is 09:50, the deduction block will be:
                deduction_block = current_time - (clock_in_object.shift_starts + 15 minutes)
                deduction_block = 09:50 - (10:00 + 00:15)
                deduction_block = 09:50 - 10:15 = -25 minutes
            if this value is less than or equal to zero, then we can surmise that the staff is early, because they are
            clocking in before any deductions will be  registered by the system.

    - hours_to_deduction: once we have established that a staff has come late, the next thing we must conclude is
            how much to deduct from their salary. this value is calculated by taking a look at how many hours late
            from the deduction time they are. so, if a shift starts at 10:00, and the  time is 10:30, hours_to_deduct:
                hours_to_deduct = divmod(deduction_block.total_seconds(), 3600)[0]
                hours_to_deduct = divmod(15minutes.total_seconds(), 3600)[0]
                hours_to_deduct = 0
            in this case, the staff has not yet reached the next hour within the deduction block, so only one hour worth
            of salary will be deducted, and so on for every hour as shown in the function.


    :param request:
    :param clock_in_id: the id of the current clock in object that is to be manipulated
    :return: django render object
    """
    gym_location = float(env("FIXED_LATITUDE")), float(env("FIXED_LONGITUDE"))
    if request.POST.get("shift-activated"):
        user_location = float(request.POST.get('latitude')), float(request.POST.get('longitude'))
        km_distance_from_gym = haversine(user_location, gym_location, unit=Unit.KILOMETERS)
        print(user_location, gym_location)
        print(km_distance_from_gym)

        if km_distance_from_gym <= 0.5:
            # we always want to make sure that the user is within the set location. if they are not, then send a
            # message to them saying that they cannot clock in
            current_time = timezone.now()
            passed_clock_in_object = get_object_or_404(ClockIn, id=clock_in_id)
            deduction_block = current_time - (passed_clock_in_object.shift_starts + datetime.timedelta(minutes=15))
            print(deduction_block)

            if deduction_block.total_seconds() < 0:
                print("C1")
                passed_clock_in_object.time_clocked_in, passed_clock_in_object.status = current_time, "EA"
            else:
                print("C2")
                hours_to_deduct = int(divmod(deduction_block.total_seconds(), 3600)[0])
                passed_clock_in_object.time_clocked_in, passed_clock_in_object.status = current_time, "LTE"
                total_deduction = request.user.basic_hourly_wage
                if hours_to_deduct > 0:
                    print("C3")
                    total_deduction += (total_deduction * hours_to_deduct)
                passed_clock_in_object.deduction = total_deduction

            passed_clock_in_object.on_shift = True
            passed_clock_in_object.save()
        else:
            # todo: log this failed clock in
            messages.error(request, "You are not within the required distance to activate your clock in. "
                                    "Please move closer to the gym before attempting to clock in")
    return redirect("schedule:clock-in")


def clock_ins_for_current_month(request, month_query, year_query):
    month_clock_ins = ClockIn.objects.annotate(monthly_count=Count('time_clocked_in')) \
        .filter(time_clocked_in__month=month_query, time_clocked_in__year=year_query,
                shift__staff_on_shift=request.user)
    month_observing = calendar.month_name[int(month_query)]
    early_clock_ins = month_clock_ins.filter(
        Q(status="EA") | Q(status="DSPS")).count()
    late_clock_ins = month_clock_ins.filter(
        Q(status="DSPF") | Q(status="LTE")
    ).count()
    date = timezone.now()
    # replaces the current date with the first date of the month and year provided in the query,
    # and then moves back by a day to find the previous month
    previous_month_data = (date.replace(day=1, month=int(month_query), year=int(year_query))) - datetime.timedelta(
        days=1)
    previous_month = previous_month_data.month
    previous_year = previous_month_data.year

    if month_query == timezone.now().month and year_query == timezone.now().year:
        end_date = timezone.now().date()
    else:
        end_date = calendar.monthrange(int(year_query), int(month_query))
        end_date = end_date[1]

    if date.month == int(month_query):
        # if the current month is the current date, then disable the next month button:
        next_button_status = "disabled"
        next_month = int(month_query)
        next_year = int(year_query)
    else:
        next_month_data = (date.replace(day=1, month=int(month_query), year=int(year_query))) + datetime.timedelta(
            days=33
        )
        next_month = next_month_data.month
        next_year = next_month_data.year
        next_button_status = ""

    all_clock_ins_count = month_clock_ins.count()
    page_object = paginator_helper(request, month_clock_ins, 10)

    context = {
        "month_clock_ins": month_clock_ins,
        "month_observing": month_observing,
        "year_observing": int(year_query),
        "early_clock_ins_count": early_clock_ins,
        "late_clock_ins_count": late_clock_ins,
        "all_clock_ins_count": all_clock_ins_count,
        "end_date": end_date,
        "previous_month_query": previous_month,
        "previous_year_query": previous_year,
        "next_month_query": next_month,
        "next_year_query": next_year,
        "next_button_disabled": next_button_status,
        "page_object": page_object
    }
    return render(request, "clock-ins-this-month.html", context)


@login_required()
def total_clock_ins(request):
    all_clock_ins = ClockIn.objects.filter(shift__staff_on_shift=request.user, time_clocked_in__isnull=False)
    early_clock_ins = all_clock_ins.filter(status="EA")
    late_clock_ins = all_clock_ins.filter(status="LTE")
    page_object = paginator_helper(request, all_clock_ins, 1)
    context = {
        "page_object": page_object,
        "early_clock_ins": early_clock_ins,
        "late_clock_ins": late_clock_ins,
    }
    return render(request, "total-clock-ins.html", context)


def clock_in_insights(request, clock_in_id):
    staff_clock_in = ClockIn.objects.filter(id=clock_in_id).select_related('shift').first()
    if staff_clock_in.shift.staff_on_shift != request.user:
        raise Http404
    else:
        return render(request, "clock-in-insights.html", {"clock_in": staff_clock_in})


def dispute_clock_in(request):
    clock_ins_to_dispute = None
    try:
        if request.GET.get("dispute-ids"):
            undisputable_clock_ins = ["EA", "CLSD", "EA", "DSP", "DSPF", "DSPS"]
            dispute_ids_as_array = request.GET.get("dispute-ids").split(",")
            clock_ins_to_dispute = ClockIn.objects.filter(id__in=dispute_ids_as_array).select_related(
                'dispute').exclude(status__in=undisputable_clock_ins)
    except AttributeError:
        raise Http404("Cannot Find any Disputes to Resolve")

    form = DisputeForm()
    file_upload = DisputeAttachmentForm()

    context = {
        "clock_ins_to_dispute": clock_ins_to_dispute,
        "form": form,
        "file_upload": file_upload
    }
    return render(request, "dispute-clock-ins.html", context)


def log_dispute(request, clock_in_id):
    if request.method == "POST" and request.POST.get("sending-form-data"):
        form = DisputeForm(request.POST, request.FILES)
        files = request.FILES.getlist('file_field')
        print(files)
        if form.is_valid():
            dispute_data = form.save(commit=False)
            try:
                with transaction.atomic():
                    clock_in_disputed = ClockIn.objects.get(id=int(clock_in_id))
                    dispute_data.clock_in = clock_in_disputed
                    description = form.cleaned_data["dispute_description"]
                    dispute_data.save()
                    for file in files:
                        DisputeAttachment.objects.create(
                            document=file, dispute=dispute_data
                        )
                    context = {
                        "dispute_description": description,
                    }
                return render(request, "partials/dispute-succeeded.html", context)
            except ClockIn.DoesNotExist:
                messages.error(request, "Unfortunately, the system could not dispute this clock in. "
                                        "Kindly report this issues to the administrator if this issue persists.")
                raise Http404("The System Could Not Log This Clock In")
        else:
            form = DisputeForm()
            # todo: partial for when the form is invalid
            messages.error(request, "Your Dispute Could Not Be Submitted")
            Http404("The System could not log this clock in")
