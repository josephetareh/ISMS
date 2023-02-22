import datetime
import calendar
from collections import deque
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import Count, Q
from django.forms import modelform_factory, modelformset_factory
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from environ import environ
from haversine import haversine, Unit

from staff_schedule.forms import DisputeForm, DisputeAttachmentForm
from staff_schedule.models import Event, Shift, ClockIn, Dispute, DisputeAttachment

env = environ.Env()


@login_required()
def personal_schedule_pass(request, schedule_weekday: str = None, activity: str = None):
    """
    :param request: django request object
    :param schedule_weekday: the current schedule weekday that the viewer is viewing provided as a string
    :param activity: the current type of event activity that hte viewer is viewing
    :return: django render object

    this view works on providing the personal schedule to each staff member. when this view is loaded, each staff
    it checks if a specific schedule weekday has been provided. in the case that this value has not been added,
    the view will provide the events for the current day of the week for the user [monday events will be shown if the
    page is visited on Monday, and so on].

    alternatively, if a specific weekday has been provided, the view will set the schedule weekday number. this number
    will be used for iterating and filtering.

    the view also allows filtering by activity (personal training, meetings, etc.). if the user does not provide an
    activity, then all activities for the specific day are displayed to the user. in the case that an activity is provided,
    then the view will filter for events based on that activity.

    the view also makes use of a deque data structure to rotate the dates, allowing the user to efficiently cycle to the
    various activities that they have on different dates.
    """
    activities = None

    # turn schedule to integer to allow it to deal with datetime objects:
    if schedule_weekday is None:
        # if there is no provided schedule date then the user should be viewing all events on the current date
        schedule_weekday = timezone.now().weekday()
        # rotate days to ensure that the current date is always going to be the first da
    else:
        # if a schedule has been provided,  the schedule date should match the corresponding database weekday choice
        date_match_dictionary = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5,
                                 "Sunday": 6}
        schedule_weekday = date_match_dictionary[schedule_weekday.title()]

    if activity is None:
        activities = Event.objects.filter(eventpersonnel__staff_on_event=request.user, event_day__day=schedule_weekday)
    else:
        activity_match_dictionary = {"Classes": "CS", "Meetings": "MT", "Personal Training": "PT"}
        activity_choice = activity_match_dictionary[activity.title()]
        activities = Event.objects.filter(eventpersonnel__staff_on_event=request.user, event_day__day=schedule_weekday,
                                          type__type=activity_choice)

    # shift the dates accordingly to ensure that the day provided is always the current date in the date queue
    date_handler = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5,
                    "Sunday": 6}
    date_shifter = deque(date_handler.items())
    date_shifter.rotate(0 - schedule_weekday)
    schedule_weekday = date_shifter[0][0]

    context = {"events": activities, "date_viewing": schedule_weekday, "activity": activity,
               "date_shifter": date_shifter}
    return render(request, "personal-schedule.html", context)


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
            activities = Event.objects.filter(eventpersonnel__staff_on_event=request.user,
                                              event_day__day=schedule_weekday). \
                select_related("type", "location", "event_day")
            activity_type = "ALL"
        else:
            activities = Event.objects.filter(eventpersonnel__staff_on_event=request.user,
                                              event_day__day=schedule_weekday,
                                              type__type=activity_type).select_related("type", "location", "event_day")
        context['activity_type'] = activity_type
        context['activities'] = activities
    else:
        schedule_weekday = timezone.now().weekday()
        activities = Event.objects.filter(eventpersonnel__staff_on_event=request.user,
                                          event_day__day=schedule_weekday, ) \
            .select_related("type", "location", "event_day")
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
    print(activities)
    return render(request, "personal-schedule.html", context)


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
        "next_button_disabled": next_button_status
    }
    return render(request, "clock-ins-this-month.html", context)


@login_required()
def total_clock_ins(request):
    all_clock_ins = ClockIn.objects.filter(shift__staff_on_shift=request.user, time_clocked_in__isnull=False)
    early_clock_ins = all_clock_ins.filter(status="EA")
    late_clock_ins = all_clock_ins.filter(status="LTE")
    context = {
        "total_clock_ins": all_clock_ins,
        "early_clock_ins": early_clock_ins,
        "late_clock_ins": late_clock_ins
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
    if request.POST and request.POST.get("sending-form-data"):
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
