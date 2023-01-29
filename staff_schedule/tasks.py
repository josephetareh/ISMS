from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from django_celery_beat.models import PeriodicTask

from staff_schedule.models import Shift, ClockIn


# @shared_task
# def clock_in_creation():
#     """
#     celery task that allows the creation of new clock ins for staff
#     :return: None
#     """
#     day_increase = timezone.now().date() + timedelta(days=7)
#     shifts = Shift.objects.filter(start_time__date=timezone.now())
#     for shift in shifts:
#         updated_clock_in = ClockIn.objects.create(shift=shift, date_to_clock_in=day_increase, status="CLSD")
#         updated_clock_in.save()


@shared_task
def set_clock_in_to_active(clock_in_identification):
    """
    celery task that will set the clock in to early at forty minutes before time
    :return:
    """
    # todo:in the case that the celery task fails to run, then we must ensure that early is displayed in JS frontend
    clock_in = ClockIn.objects.get(id=int(clock_in_identification))
    clock_in.active = True
    print("do I have a primary key", clock_in.pk)
    clock_in.save()


@shared_task
def create_fresh_clock_ins():
    """
    this task will run at 23:00 each day to ensure that fresh clock ins are created for staff that failed to clock in
    :return: None
    """
    # grab all the clock ins for the day
    clock_ins_for_the_day = ClockIn.objects.filter(shift_starts__day=timezone.now().day)
    # get all the shifts that did not have any clock in created for them
    untethered_clock_ins = []
    untethered_clock_ins_with_no_periodic_task = []
    for clock_in in clock_ins_for_the_day:
        new_start_date, new_end_date = clock_in.shift_starts + timedelta(days=7), clock_in.shift_ends + timedelta(days=7)
        new_clock_in, created = ClockIn.objects.get_or_create(shift=clock_in.shift, shift_starts=new_start_date)
        if not created:
            untethered_clock_ins.append(clock_in)
            new_clock_in.save()
            # remove the periodic task for the clock ins
            try:
                periodic_task_for_clock_in = PeriodicTask.objects.get(name=f"clock id = {clock_in.id}")
                periodic_task_for_clock_in.delete()
            except PeriodicTask.DoesNotExist:
                untethered_clock_ins_with_no_periodic_task.append(clock_in)
    # todo: send mail for both arrays if their len is > 0
