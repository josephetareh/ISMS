import datetime
from collections import deque

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from staff_schedule.models import Event


@login_required()
def personal_schedule(request, schedule_date=None, activity=None):
    """
    :param request:
    :param schedule_date:
    :param activity:
    :return:
    """
    activities = None

    # turn schedule to integer to allow it to deal with datetime objects:
    if schedule_date is None:
        # if there is no provided schedule date then the user should be viewing all events on the current date
        schedule_date = datetime.datetime.now().weekday()
        # rotate days to ensure that the current date is always going to be the first da
    else:
        # if a schedule has been provided,  the schedule date should match the corresponding database weekday choice
        date_match_dictionary = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5,
                                 "Sunday": 6}
        schedule_date = date_match_dictionary[schedule_date.title()]

    if activity is None:
        activities = Event.objects.filter(eventpersonnel__staff_on_event=request.user, event_day__day=schedule_date)
    else:
        activity_match_dictionary = {"Classes": "CS", "Meetings": "MT", "Personal Training": "PT"}
        activity_choice = activity_match_dictionary[activity.title()]
        activities = Event.objects.filter(eventpersonnel__staff_on_event=request.user, event_day__day=schedule_date,
                                          type__type=activity_choice)

    # shift the dates accordingly to ensure that the day provided is always the current date in the date queue
    date_handler = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5,
                    "Sunday": 6}
    date_shifter = deque(date_handler.items())
    date_shifter.rotate(0 - schedule_date)
    schedule_date = date_shifter[0][0]
    print(schedule_date)

    context = {"events": activities, "date_viewing": schedule_date, "activity": activity, "date_shifter": date_shifter}
    return render(request, "personal-schedule.html", context)

# @login_required()
# def personal_schedule(request, schedule_date=None, event_type="all"):
#     """
#
#     :param event_type:
#     :param schedule_date:
#     :param request:
#     :return:
#     """
#     user = request.user
#
#     if schedule_date is None:
#         # if there is no date provided return the current date
#         numerical_representation = datetime.datetime.now()
#         string_representation = numerical_representation.strftime("%A")
#         previous_day = 7 if numerical_representation.weekday() - 1 < 0 else numerical_representation.weekday() - 1
#         next_day = 0 if numerical_representation.weekday() + 1 > 6 else numerical_representation.weekday() + 1
#         matching_day = (numerical_representation.weekday(), string_representation, previous_day, next_day)
#     else:
#         numerical_representation = schedule_date
#         numerical_match = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday",
#                            6: "Sunday"}
#         previous_day = 7 if numerical_representation - 1 < 0 else numerical_representation - 1
#         next_day = 0 if numerical_representation + 1 > 6 else numerical_representation + 1
#         string_representation = numerical_match[numerical_representation]
#         matching_day = (numerical_representation, string_representation, previous_day, next_day)
#
#     daily_events = Event.objects.filter(event_day__day=numerical_representation)
#
#     if request.htmx and request.POST.get("event-filter") == "all" or event_type == "all":
#         user_schedule = daily_events.filter(eventpersonnel__staff_on_event=user)
#     elif request.htmx and request.POST.get("event-filter") == "MTS" or event_type == "MTS":
#         user_schedule = daily_events.filter(eventpersonnel__staff_on_event=user, type__type="MT")
#     elif request.htmx and request.POST.get("event-filter") == "PT" or event_type == "PT":
#         user_schedule = daily_events.filter(eventpersonnel__staff_on_event=user, type__type="PT")
#     elif request.htmx and request.POST.get("event-filter") == "CLS" or event_type == "CLS":
#         user_schedule = daily_events.filter(eventpersonnel__staff_on_event=user, type__type="CS")
#     else:
#         user_schedule = daily_events.filter(eventpersonnel__staff_on_event=user)
#
#     context = {"user_schedule": user_schedule, "current_date_viewing": matching_day, "event_type": event_type}
#     return render(request, "personal_schedule.html", context)
#
