import json
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from payments.models import PaySlip


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
    # todo: before migration — probably want to change this name to prevent python clash errors
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
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    staff_working = models.ManyToManyField(settings.AUTH_USER_MODEL, through="EventPersonnel",
                                           through_fields=('event', 'staff_on_event'))
    event_day = models.ForeignKey(Weekday, null=False, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=12, blank=True, null=True)

    # positive integer field here to show how many times the event will be recurring for.
    # another field to say that the recurring of the event is true

    # covering = models.BooleanField(default=False)

    def __str__(self):
        return self.event_name

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)
        self.slug = f"{self.type.type}-ID-{self.location.location_name}-{self.id}"
        super().save(*args, **kwargs)


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


class GroupClass(models.Model):
    class_name = models.CharField(max_length=100, blank=False)
    description = models.TextField(max_length=1000, blank=True)
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                limit_choices_to={
                                    "groups__name": "Trainer"
                                })

    def __str__(self):
        return self.class_name


class GroupClassPayment(models.Model):
    payment_for_class = models.ForeignKey(GroupClass, on_delete=models.SET_NULL, null=True, blank=True)
    attendees = models.PositiveIntegerField(default=0, blank=True, null=True)
    attendance_logged = models.BooleanField(default=False)
    payment_request_created = models.DateTimeField(auto_now_add=True)
    time_of_payment = models.DateTimeField(null=True, blank=True)
    class_paid_for = models.BooleanField(default=False)
    total_payment = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    sent_for_payment = models.BooleanField(default=False)
    payslip = models.ForeignKey(PaySlip, null=True, blank=True, on_delete=models.SET_NULL)


class Meeting(models.Model):
    meeting_title = models.CharField(max_length=100, blank=False)
    description = models.TextField(max_length=3000, blank=False)
    staff_attending = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.meeting_title


class ISMSSchedule(models.Model):
    RECURRING_CHOICES = [
        ("DLY", "Daily"),
        ("WKLY", "Weekly"),
        ("MTH", "Monthly")
    ]
    EVENT_TYPES = [
        ("CS", "Class"),
        ("MT", "Meeting"),
        ("PT", "Personal Training Session")
    ]
    WEEKDAYS = [
        ("0", "Monday"),
        ("1", "Tuesday"),
        ("2", "Wednesday"),
        ("3", "Thursday"),
        ("4", "Friday"),
        ("5", "Saturday"),
        ("6", "Sunday")
    ]
    LOCATIONS = [
        ("OF", "Office"),
        ("MTA", "Multi-Tasking Area"),
        ("SA", "Strength Area"),
        ("ISMS", "ISMS Platform"),
        ("CA", "Class Area")
    ]
    schedule_type = models.CharField(choices=EVENT_TYPES, max_length=2)
    schedule_day = models.CharField(choices=WEEKDAYS, max_length=1)
    group_class = models.ForeignKey(GroupClass, on_delete=models.CASCADE, null=True, blank=True)
    staff_meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, null=True, blank=True)
    location = models.CharField(choices=LOCATIONS, max_length=4)
    slug = models.SlugField(max_length=20, blank=True, null=True, unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    recurring = models.BooleanField(default=False)
    recurring_interval = models.CharField(
        choices=RECURRING_CHOICES, max_length=4
    )
    recurring_count = models.PositiveIntegerField(default=0, blank=True, null=True)

    def __str__(self):
        if self.group_class:
            return str(self.group_class)
        elif self.staff_meeting:
            return str(self.staff_meeting)
        else:
            return super().__str__()
            # return super(ISMSSchedule, self).__str__()

    def save(self, *args, **kwargs):
        if self.pk is None:
            super().save(*args, **kwargs)
        # set the event type dynamically
        if self.group_class:
            self.schedule_type = "CS"
        elif self.staff_meeting:
            self.schedule_type = "MT"

        self.slug = f"{self.schedule_type}-ID-{self.location}-{self.id}"

        # todo: recurring functionality

        # todo: validation rules:
        #   — ensure that self.group_class and self.staff_meeting cannot be together
        #   — ensure that the start_date and end_date are always the same date and it matches the weekday choice
        #   — if the recurring interval has been set, then you must not be able to set a recurring schedule.
        #   they are not compatible
        super().save(*args, **kwargs)


class Shift(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    staff_on_shift = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    weekday = models.ForeignKey(Weekday, null=True, blank=True, on_delete=models.CASCADE)

    # todo shift covering functionality here test for normalization

    def __str__(self):
        return "{} starting at {} and ending at {}".format(self.staff_on_shift,
                                                           self.start_time.time(),
                                                           self.end_time.time())

    def save(self, *args, **kwargs):
        current_weekday = self.start_time.weekday()
        self.weekday = Weekday.objects.get(day=str(current_weekday))
        if self.pk is None:
            # todo: ensure that any changes to the shift will affect any clock ins posted — generally will be a maximum
            #  of 2 the current one and the one that may have been created automatically with celery. this will prevent
            #  scenarios where multiple clock ins will be created after a shift has been changed
            super().save(*args, **kwargs)
            corresponding_clockin, _ = ClockIn.objects.get_or_create(shift=self, status="CLSD",
                                                                     shift_starts=self.start_time,
                                                                     shift_ends=self.end_time)
            corresponding_clockin.save()
        super().save(*args, **kwargs)


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
    payment_for_shift = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
    deduction = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
    final_payment = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
    payslip = models.ForeignKey(PaySlip, blank=True, null=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):

        time_to_shift_beginning = abs(timezone.now() - self.shift_starts).total_seconds()
        if timezone.now() >= self.shift_starts:
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
            else:
                self.active = False

        time_difference = self.shift_ends - self.shift_starts
        hours = divmod(time_difference.total_seconds(), 3600)
        print("HI", hours)
        minute_payment_for_shift = 0
        hourly_payment_for_shift = Decimal(self.shift.staff_on_shift.basic_hourly_wage) * Decimal(hours[0])
        if hours[1] > 0:
            minute_payment_for_shift = Decimal((hours[1] / 60)) * self.shift.staff_on_shift.basic_hourly_wage
        # todo: may want to round this down to the nearest whole number
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
            this is functionality to create a new periodic task that will run the first time a clock in is created
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
            try:
                """
                try-except block to handle scenarios where a PeriodicTask may have been deleted
                """
                current_corresponding_periodic_task = PeriodicTask.objects.get(
                    name=f"clock id = {self.id}",
                )
            except PeriodicTask.DoesNotExist:
                current_corresponding_periodic_task = None

            if current_corresponding_periodic_task is not None \
                    and current_corresponding_periodic_task.crontab != schedule:
                # if a PeriodicTask currently exists, but there is a different schedule, then we have to delete
                # the matching PeriodicTask because it will run at the wrong time otherwise.
                current_corresponding_periodic_task.delete()
                current_corresponding_periodic_task = None

            if current_corresponding_periodic_task is None:
                # once the PeriodicTask has been deleted, or if it was never found:
                PeriodicTask.objects.create(
                    name=f'clock id = {self.id}',
                    crontab=schedule,
                    task='staff_schedule.tasks.set_clock_in_to_active',
                    args=json.dumps([f'{self.id}'])
                )

            if self.on_shift:

                self.final_payment = self.payment_for_shift - self.deduction

                # when a staff begins a shift, a new clock in must be created for the
                # corresponding  week after. in the future, we will need to ensure that
                # this checks for covering status
                new_start_date, new_end_date = \
                    self.shift_starts + timedelta(days=7), self.shift_ends + timedelta(days=7)
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


class Dispute(models.Model):
    status = [
        ("FL", "Failed"),
        ("PND", "Pending"),
        ("SUC", "Success")
    ]
    clock_in = models.OneToOneField(ClockIn, on_delete=models.CASCADE, primary_key=True)
    dispute_status = models.CharField(choices=status, max_length=3, blank=True, default="PND")
    date_disputed = models.DateTimeField(auto_now_add=True)
    dispute_description = models.TextField(max_length=400, blank=True, null=True)
    dispute_reply = models.TextField(max_length=1000, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.date_disputed is None:
            # on the first instance of creation (when the date disputed is none)
            # — change the status of the clock in to disputing
            # TODO: SERIOUS — POST TESTING:
            self.clock_in.status = "DSP"
            self.clock_in.save()
        super().save(*args, **kwargs)


def dispute_upload_directory_path(instance, filename):
    return f"disputes/attachments/clock-in-{instance.dispute.clock_in.id}/{filename}"


class DisputeAttachment(models.Model):
    description = models.CharField(max_length=280, blank=True)
    document = models.FileField(upload_to=dispute_upload_directory_path, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE, blank=False, null=False)
