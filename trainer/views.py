from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils import timezone

from conf.helper_functions import paginator_helper
from conf.url_tests import trainer_test
from staff_schedule.forms import AddExerciseForm
from staff_schedule.models import ISMSScheduleCalendarEvent, TrainingSessionInfo
from trainer.models import ClientTrainerRelationship, Client, SessionExercises, TrainerSession


@login_required()
@user_passes_test(trainer_test)
def my_clients(request):
    client_list = ClientTrainerRelationship.objects.filter(
        trainer=request.user,
    ).prefetch_related("client")
    page_object = paginator_helper(request, client_list, 9)
    context = {
        "page_object": page_object
    }
    return render(request, "my-clients.html", context)


@login_required()
@user_passes_test(trainer_test)
def my_sessions(request, calendar_event_identification, slug_details):
    context = {}
    current_page_url = request.get_full_path().split("/")
    current_page_id, current_page_slug = current_page_url[3], current_page_url[4]
    calendar_event = ISMSScheduleCalendarEvent.objects.get(
        id=int(calendar_event_identification)
    )
    current_time = timezone.now()
    if request.POST and request.POST.get("starting-session-for"):
        starting_session_for_values = request.POST.get("starting-session-for")
        if starting_session_for_values:
            with transaction.atomic():
                selected_identification_numbers = starting_session_for_values.split(", ")
                TrainingSessionInfo.objects.filter(personal_training_event_id__in=selected_identification_numbers). \
                    update(session_started=True, session_start_time=current_time)
                calendar_event.started = True
                calendar_event.save()
    if request.POST and request.POST.get("ending-session-for"):
        ending_session_for_value = request.POST.get("ending-session-for")
        if ending_session_for_value:
            training_session = TrainingSessionInfo.objects.get(
                id=int(ending_session_for_value)
            )
            training_session.session_end_time = current_time
            training_session.save()

    attached_sessions = TrainingSessionInfo.objects.filter(
        calendar_event_id=int(calendar_event_identification),
        personal_training_event__trainer=request.user
    ).prefetch_related("personal_training_event", "personal_training_event__client")

    sessions_not_started = []
    for session in attached_sessions:
        if not session.session_started:
            sessions_not_started.append(session.id)
    # attached_sessions_ids = [session.id for session in started_sessions_exclude]
    ids_as_string = ", ".join(str(id_number) for id_number in sessions_not_started)

    if attached_sessions:
        if calendar_event.start_date.date() == current_time.date() and current_time >= (
                calendar_event.start_date - timedelta(minutes=30)):
            # trainer can start the session if they have not already started it in the past:
            context['can_start_session'] = False if calendar_event.started else True
        else:
            context['can_start_session'] = False

    context["add_exercises_form"] = AddExerciseForm()
    context['attached_sessions'] = attached_sessions
    context['attached_sessions_ids'] = ids_as_string
    context['current_id'] = int(current_page_id)
    context['current_slug'] = current_page_slug
    context["calendar_event"] = calendar_event
    return render(request, "my-sessions.html", context)


def add_exercise(request, calendar_event_identification, slug_details):
    if request.POST:
        # todo: think about model form here
        form = AddExerciseForm(request.POST)
        if form.is_valid():
            # print(request.POST.get("choose-users"))
            users_editing = request.POST.get("choose-users")
            with transaction.atomic():
                new_training_exercise = form.save()
                if users_editing != "all":
                    session_to_update = TrainingSessionInfo.objects.get(
                        calendar_event_id=int(calendar_event_identification),
                        personal_training_event_id=int(users_editing)
                    )
                    session_to_update.exercises_performed.add(new_training_exercise)
                    session_to_update.save()
                else:
                    sessions_to_update = TrainingSessionInfo.objects.filter(
                        calendar_event_id=int(calendar_event_identification)
                    )
                    for session in sessions_to_update:
                        session.exercises_performed.add(new_training_exercise)
                        session.save()
            return redirect("trainer:my-sessions",
                            calendar_event_identification=calendar_event_identification,
                            slug_details=slug_details)
