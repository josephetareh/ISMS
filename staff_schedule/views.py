import datetime
from collections import deque
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from haversine import haversine, Unit

from staff_schedule.models import Event, Shift, ClockIn

User = get_user_model()


@login_required()
def personal_schedule(request, schedule_weekday: str = None, activity: str = None):
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
def update_shifts():
    # todo: add role requirements to this
    pass


@login_required()
def clock_in(request):
    """
    view that shows the clock in for each staff
    :param request:
    :return:
    """

    current_time = timezone.now()  # todo: move to JS
    fixed_latitude, fixed_longitude = 8.96759493449641, 7.465179361162659
    gym_location = (fixed_latitude, fixed_longitude)

    # grab the nearest active shift
    next_clock_in = ClockIn.objects.filter(shift__staff_on_shift=request.user,
                                           shift_ends__gte=timezone.now()).order_by('shift_starts').first()
    if next_clock_in:
        time_to_open = next_clock_in.shift_starts - datetime.timedelta(minutes=40)

        # button_status = {"button_id": "", "button display": "clock in"}
        if not next_clock_in.on_shift:
            if next_clock_in.active:
                button_status = ("", "clock-in-enabled")
            else:
                button_status = ("disabled", "clock-in-disabled")
        else:
            button_status = ("", "staff-on-shift")

        if request.POST.get("shift-activated"):
            user_latitude = float(request.POST.get("latitude"))
            user_longitude = float(request.POST.get("longitude"))
            user_location = (user_latitude, user_longitude)
            km_distance_from_gym = haversine(user_location, user_location, unit=Unit.KILOMETERS)

            if km_distance_from_gym <= 0.5:
                # firstly, we want to make sure that the user is within the set location
                # if the user activates the shift then run this bit of code
                next_clock_in.on_shift = True
                time_difference = timezone.now() - next_clock_in.shift_starts
                deduction_block = timezone.now() - (next_clock_in.shift_starts + datetime.timedelta(minutes=15))
                time_block_hours = int(divmod(deduction_block.total_seconds(), 3600)[0])

                # if the shift is activated before time, then mark it as early with no deduction
                if (timezone.now() <= next_clock_in.shift_starts) or (time_difference.total_seconds() <= 900):
                    # shift is marked at least 15 minutes within the running time so the shift is marked as early
                    next_clock_in.time_clocked_in, next_clock_in.status = timezone.now(), "EA"
                else:
                    # shift is marked more than 15 minutes after the running time so the shift is marked as late
                    next_clock_in.time_clocked_in, next_clock_in.status = timezone.now(), "LTE"
                    total_deduction = request.user.basic_hourly_wage
                    if time_block_hours > 0:
                        # for every additional hour that the shift is run, the user loses that hourly wage.
                        total_deduction += (request.user.basic_hourly_wage * time_block_hours)
                    next_clock_in.deduction = total_deduction
            else:
                messages.error(request, "you are not within the required distance to activate your clock in. "
                                        "please move closer to the gym before attempting to clock in")
                print("erroring")
        next_clock_in.save()

        context = {
            "current_time": current_time,
            "active_clock_in": next_clock_in,
            "time_to_open": time_to_open,
            "clock_in_button_info": button_status
        }
    else:
        context = {
            "active_clock_in": None
        }
    return render(request, 'clock-in.html', context)
