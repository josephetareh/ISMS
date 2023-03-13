import json
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from django.db.models import Q
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from payments.models import PaySlip
from trainer.models import Client, TrainerSession, GroupClass, SessionExerciseItem


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


class Meeting(models.Model):
    meeting_title = models.CharField(max_length=100, blank=False)
    description = models.TextField(max_length=3000, blank=False)
    staff_attending = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.meeting_title


class ISMSScheduleFixedEvent(models.Model):
    RECURRING_CHOICES = [
        ("DLY", "Daily"),
        ("WKLY", "Weekly"),
        ("MTH", "Monthly")
    ]
    EVENT_TYPES = [
        ("CS", "Class"),
        ("MT", "Meeting"),
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
    schedule_day = models.CharField(choices=WEEKDAYS, max_length=1, blank=True)
    group_class = models.ForeignKey(GroupClass, on_delete=models.CASCADE, null=True, blank=True)
    staff_meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, null=True, blank=True)
    location = models.CharField(choices=LOCATIONS, max_length=4)
    slug = models.SlugField(max_length=20, blank=True, null=True, unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    # # todo: implementing this functionality
    # recurring = models.BooleanField(default=False)
    # recurring_interval = models.CharField(
    #     choices=RECURRING_CHOICES, max_length=4
    # )
    # recurring_count = models.PositiveIntegerField(default=0, blank=True, null=True)

    def __str__(self):
        if self.group_class:
            return str(self.group_class)
        elif self.staff_meeting:
            return str(self.staff_meeting)
        else:
            return super().__str__()

    def clean(self):
        if self.staff_meeting and self.group_class:
            raise ValidationError("You May Only Select One Type of Event for a Fixed Schedule Item")
        if self.start_time.weekday() != self.end_time.weekday():
            raise ValidationError("ISMS Fixed Events May Only Occur on a Single Date. "
                                  "Please Ensure that Both the Start and End Time are On The Same Date")

    def save(self, *args, **kwargs):
        self.schedule_day = str(self.start_time.weekday())
        if self.pk is None:
            super().save(*args, **kwargs)

        if self.group_class:
            self.schedule_type = "CS"
        elif self.staff_meeting:
            self.schedule_type = "MT"

        self.slug = f"{self.schedule_type}-ID-{self.location}-{self.id}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "ISMS Schedule Fixed Event"


# class CalendarEvent(models.Model):
#     start_time = models.DateTimeField()
#     end_time = models.DateTimeField()


class ISMSScheduleCalendarEvent(models.Model):
    CALENDAR_EVENT_SCHEDULE_TYPES = [
        ("MT", "Meeting"),
        ("SPE", "Special Event"),
        ("PT", "Personal Training"),
        ("CS", "Class")
    ]
    schedule_type = models.CharField(choices=CALENDAR_EVENT_SCHEDULE_TYPES, max_length=3)
    personal_training_event = models.ManyToManyField(TrainerSession, blank=True, through='TrainingSessionInfo')
    # todo: add class here — this will be used in cases where a trainer is covering for a class.
    meeting_event = models.ForeignKey(Meeting, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    slug = models.SlugField(max_length=400, blank=True)
    started = models.BooleanField(default=False)
    ended = models.BooleanField(default=False)


    def clean(self):
        # if self.pk:
        #     # todo: move this functionality to view on creation
        #     if self.personal_training_event and self.meeting_event:
        #         raise ValidationError("You May Only Select One Type of Event for a Calendar Event")
        if self.start_date.weekday() != self.end_date.weekday():
            raise ValidationError("ISMS Calendar Events May Only Occur Over the Course of a Single Day")

    def save(self, *args, **kwargs):
        if self.pk is None:
            # each time that a PT sessions is added to the calendar, it must be reduced by one:
            # todo: each time that a PT session is deleted from the calendar, one should be added to it
            super().save(*args, **kwargs)
            # test this:
            # todo: this functionality will have to be moved to the view / form:
            if self.personal_training_event:
                for event in self.personal_training_event.all():
                    try:
                        event.sessions_left -= 1
                        if event.sessions_left == 0:
                            raise ValidationError(f"No More Sessions Can Be Allocated For {event}")
                        event.save()
                    except IntegrityError:
                        raise ValidationError(f"No More Sessions Can Be Allocated For {event}")

        if not self.slug:
            self.slug = f"ISMS-Calendar-Event-{self.id}-{self.schedule_type}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "ISMS Schedule Calendar Event"


class TrainingSessionInfo(models.Model):
    personal_training_event = models.ForeignKey(TrainerSession, on_delete=models.CASCADE)
    calendar_event = models.ForeignKey(ISMSScheduleCalendarEvent, on_delete=models.CASCADE)
    session_started = models.BooleanField(default=False)
    session_start_time = models.DateTimeField(null=True, blank=True)
    session_end_time = models.DateTimeField(null=True, blank=True)
    exercises_performed = models.ManyToManyField(SessionExerciseItem)


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
