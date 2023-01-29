import json
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class Location(models.Model):
    # todo: on final version — reflect locations
    LOCATIONS = [
        ("OF", "Office"),
        ("MTA", "Multi-Tasking Area"),
        ("SA", "Strength Area"),
        ("ISMS", "ISMS Platform"),
        ("CA", "Class Area")
    ]
    location_name = models.CharField(max_length=4, choices=LOCATIONS)

    def __str__(self):
        return self.get_location_name_display()


class EventType(models.Model):
    EVENT_TYPES = [
        ("CS", "Classes"),
        ("MT", "Meeting"),
        ("PT", "Personal Training")
    ]
    type = models.CharField(max_length=2, choices=EVENT_TYPES)

    def __str__(self):
        return self.get_type_display()


class Weekday(models.Model):
    WEEKDAYS = [
        ("0", "Monday"),
        ("1", "Tuesday"),
        ("2", "Wednesday"),
        ("3", "Thursday"),
        ("4", "Friday"),
        ("5", "Saturday"),
        ("6", "Sunday")
    ]
    day = models.CharField(max_length=1, choices=WEEKDAYS)

    def __str__(self):
        return self.get_day_display()


class Event(models.Model):
    event_name = models.CharField(max_length=300, blank=False)
    description = models.TextField(max_length=1000, blank=True, null=True)
    type = models.ForeignKey(EventType, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    staff_working = models.ManyToManyField(settings.AUTH_USER_MODEL, through="EventPersonnel",
                                           through_fields=('event', 'staff_on_event'))
    event_day = models.ForeignKey(Weekday, null=False, on_delete=models.CASCADE)

    # positive integer field here to show how many times the event will be recurring for.
    # another field to say that the recurring of the event is true

    # covering = models.BooleanField(default=False)

    def __str__(self):
        return self.event_name


class EventPersonnel(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    staff_on_event = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    covering_for = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE,
                                     related_name="staff_covering_for")
    covering = models.BooleanField(default=False)
    covering_duration = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        string_representation = "{} for {}"
        return string_representation.format(self.event, self.staff_on_event)


class Shift(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    staff_on_shift = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # todo — remove this
    shift_weekday = models.ForeignKey(Weekday, on_delete=models.CASCADE, blank=False, null=False)

    # todo shift covering functionality here test for normalization

    def __str__(self):
        return "{} shift for {} starting at {} and ending at {}".format(self.shift_weekday, self.staff_on_shift,
                                                                        self.start_time.time(),
                                                                        self.end_time.time())

    def save(self, *args, **kwargs):
        if self.pk is None:
            # todo: ensure that any changes to the shift will affect any clock ins posted — generally will be a maximum
            #  of 2 the current one and the one that may have been created automatically with celery. this will prevent
            #  scenarios where multiple clock ins will be created after a shift has been changed
            super().save(*args, **kwargs)
            corresponding_clockin, _ = ClockIn.objects.get_or_create(shift=self, status="CLSD",
                                                                     shift_starts=self.start_time,
                                                                     shift_ends=self.end_time)
            corresponding_clockin.save()


class ClockIn(models.Model):
    """
    :status: indicates the different status that a clock in could have
    :shift: indicates the shift that the clock in is linked to
    :time_clocked_in: indicates the time that the user has clocked in. value will be used to calculate total pay
    :active: indicates whether a clock in is open or closed
    :on_shift: indicates whether a staff is currently on a shift or not
    :paid: indicates the total amount that a staff has been paid for that shift
    :deduction: indicates the total amount that a staff has been deducted if they showed up late for the shift
    """
    # todo: in future migrations, closed should become inactive as this is a better descriptor
    status = [
        ("CLSD", "Closed"),
        ("EA", "Early"),
        ("LTE", "Late"),
        ("DSP", "Disputing"),
        ("DSPF", "Dispute Failed"),
        ("DSPS", "Dispute Succeeded")
    ]
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True)
    shift_starts = models.DateTimeField(blank=True, null=True)
    shift_ends = models.DateTimeField(blank=True, null=True)
    time_clocked_in = models.DateTimeField(blank=True, null=True)
    status = models.CharField(choices=status, max_length=4, blank=False, null=False, default="CLSD")
    active = models.BooleanField(default=False)
    on_shift = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    # todo: in future migrations, change this to a decimal
    payment_for_shift = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
    deduction = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):

        time_to_shift_beginning = (timezone.now() - self.shift_starts).total_seconds()
        if time_to_shift_beginning >= 0:
            # if the current time is greater than the start of the shift then activate the shift
            self.active = True
        else:
            # if the current time is not greater than the shift, but it is within 40 minutes,
            # then also activate the shift. this will be necessary in cases where a new shift is created
            # for new staff and celery does not ever get a chance to run.
            if divmod(time_to_shift_beginning, 3600)[0] == 0:
                if divmod(time_to_shift_beginning, 60)[0] <= 40:
                    self.active = True
            else:
                self.active = False



        # todo: post testing, only run this on the first instance of the clock in creation
        time_difference = self.shift_ends - self.shift_starts
        hours = divmod(time_difference.total_seconds(), 3600)
        minute_payment_for_shift = 0
        hourly_payment_for_shift = Decimal(self.shift.staff_on_shift.basic_hourly_wage) * Decimal(hours[0])
        if hours[1] > 0:
            minute_payment_for_shift = Decimal((hours[1] / 3600)) * self.shift.staff_on_shift.basic_hourly_wage
        self.payment_for_shift = minute_payment_for_shift + hourly_payment_for_shift

        # set up for the periodic tasks:
        time_to_open = self.shift_starts - timedelta(minutes=40)
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute=str(time_to_open.minute),
            hour=str(time_to_open.hour),
            day_of_week=str(time_to_open.strftime("%A")),
            day_of_month=str(time_to_open.day),
            month_of_year=str(time_to_open.month),
        )

        if self.pk is None:
            """
            this is functionality to create a new periodic task that will run when a clock moves from being closed
            to opened
            """
            # save is called here because the primary key is needed to be able to create a unique Periodic Task
            super().save(*args, **kwargs)

            # only create a corresponding periodic task for new clock ins
            # todo : make one off periodic task after testing is concluded
            PeriodicTask.objects.create(
                name=f'clock id = {self.id}',
                crontab=schedule,
                task='staff_schedule.tasks.set_clock_in_to_active',
                args=json.dumps([f'{self.id}'])
            )
        else:
            # ensure that the Periodic Task changes if the clock in data changes
            try:
                current_corresponding_periodic_task = PeriodicTask.objects.get(
                    name=f"clock id = {self.id}",
                )
            except PeriodicTask.DoesNotExist:
                current_corresponding_periodic_task = None

            if current_corresponding_periodic_task is not None:
                # delete the current corresponding periodic task to allow set a new one if one already exists
                current_corresponding_periodic_task.delete()

            if current_corresponding_periodic_task is None or current_corresponding_periodic_task.crontab != schedule:
                # if the crontab is different, delete the old periodic task associated to this clock in and
                # create a new one as the time data has been changed for the clock in
                PeriodicTask.objects.create(
                    name=f'clock id = {self.id}',
                    crontab=schedule,
                    task='staff_schedule.tasks.set_clock_in_to_active',
                    args=json.dumps([f'{self.id}'])
                )

            if self.on_shift:
                # for view purposes, we always want to ensure that when a staff is on shift,
                # the clock in can no longer be marked as activate-able
                self.active = False

                # when a staff begins a shift, a new clock in must be created for the
                # corresponding  week after. in the future, we will need to ensure that
                # this checks for covering status
                new_start_date, new_end_date = self.shift_starts + timedelta(days=7), \
                                               self.shift_ends + timedelta(days=7)
                new_clockin, created = ClockIn.objects.get_or_create(shift=self.shift, status="CLSD",
                                                                     shift_starts=new_start_date,
                                                                     shift_ends=new_end_date)
                new_clockin.save()
                try:
                    # delete the initial periodic task that marked this clock in as active.
                    periodic_task_for_clockin = PeriodicTask.objects.get(name=f"clock id = {self.id}")
                    periodic_task_for_clockin.delete()
                except PeriodicTask.DoesNotExist:
                    # todo: send mail saying that a periodic task weirdly does not exist
                    pass
            super().save(*args, **kwargs)
