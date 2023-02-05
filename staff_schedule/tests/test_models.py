# todo: django-webtest, coverage, and django-discover-runner
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from staff_schedule.models import Location, EventType, Weekday, Event, Shift, ClockIn


class StaffScheduleTests(TestCase):
    def setUp(self):
        Location.objects.create(location_name="OF")
        EventType.objects.create(type="CS")
        weekday_setup = Weekday.objects.create(day="0")
        user = get_user_model()
        self.user = user.objects.create(email="normal@user.com", username="normal", password="foo",
                                        basic_hourly_wage=300)
        # todo: make this a class level attribute
        shift_starting_time = timezone.now()
        shift_ending_time = timezone.now() + timedelta(hours=2, minutes=40)
        Shift.objects.create(
            start_time=shift_starting_time,
            end_time=shift_ending_time,
            staff_on_shift=self.user,
            shift_weekday=weekday_setup
        )

    def test_location_name_display(self):
        office_location = Location.objects.get(location_name="OF")
        self.assertEqual(str(office_location), "Office")

    def test_event_type_display(self):
        event_type = EventType.objects.get(type__exact="CS")
        self.assertEqual(str(event_type), "Classes")

    def test_weekday_display(self):
        monday_weekday = Weekday.objects.get(day="0")
        self.assertEqual(str(monday_weekday), "Monday")

    def test_shift_clock_in_creation(self):
        weekday_setup = Weekday.objects.create(day="0")
        starting_time = timezone.now()
        ending_time = timezone.now() + timedelta(minutes=40)
        test_shift = Shift(
            start_time=starting_time,
            end_time=ending_time,
            shift_weekday=weekday_setup,
            staff_on_shift=self.user,

        )

        with self.assertRaises(ClockIn.DoesNotExist) as cm:
            corresponding_clock_in = ClockIn.objects.get(
                shift=test_shift,
                shift_starts=starting_time,
                shift_ends=ending_time,
                status="CLSD",
            )
            self.assertEqual("ClockIn matching query does not exist", cm.exception)
            test_shift.save()
            self.assertIsNotNone(corresponding_clock_in)


class TestClockInPeriodicTasks(TestCase):
    def setUp(self):
        self.starting_time = timezone.now()
        self.ending_time = timezone.now() + timedelta(minutes=40)
        self.weekday_setup = Weekday.objects.create(day=0)
        self.user = get_user_model().objects.create(
            email="normal@user.com", username="normal", password="foo",
            basic_hourly_wage=300
        )
        self.test_shift = Shift.objects.create(
            start_time=self.starting_time,
            end_time=self.ending_time,
            shift_weekday=self.weekday_setup,
            staff_on_shift=self.user
        )

    def test_creation_of_corresponding_clockin(self):
        """
        This task test whether a corresponding Periodic Task is always created with a clock in
        :return:
        """
        test_clock_in = ClockIn(
            shift=self.test_shift,
            shift_starts=self.starting_time,
            shift_ends=self.ending_time,
            status="CLSD"
        )
        with self.assertRaises(PeriodicTask.DoesNotExist):
            PeriodicTask.objects.get(
                name=f"clock id = {test_clock_in.id}"
            )
        test_clock_in.save()

    def test_ensure_periodic_task_changes(self):
        test_clock_in = ClockIn.objects.create(
            shift=self.test_shift,
            shift_starts=self.starting_time,
            shift_ends=self.ending_time,
            status="CLSD"
        )
        corresponding_periodic_task = PeriodicTask.objects.get(
            name=f"clock id = {test_clock_in.id}"
        )
        time_to_open = test_clock_in.shift_starts - timedelta(minutes=40)
        matching_schedule, created = CrontabSchedule.objects.get_or_create(
            minute=str(time_to_open.minute),
            hour=str(time_to_open.hour),
            day_of_week=str(time_to_open.strftime("%A")),
            day_of_month=str(time_to_open.day),
            month_of_year=str(time_to_open.month),
        )
        self.assertEqual(corresponding_periodic_task.crontab, matching_schedule)
        corresponding_periodic_task.delete()
        # change clock in value:
        test_clock_in.shift_starts = self.starting_time - timedelta(minutes=40)
        with self.assertRaises(PeriodicTask.DoesNotExist):
            PeriodicTask.objects.get(
                name=f"clock id = {test_clock_in.id}"
            )
        test_clock_in.save()

    def test_ensure_periodic_task_always_created(self):
        test_clock_in = ClockIn.objects.create(
            shift=self.test_shift,
            shift_starts=self.starting_time,
            shift_ends=self.ending_time,
            status="CLSD"
        )
        old_periodic_task = PeriodicTask.objects.get(
            name=f"clock id = {test_clock_in.id}"
        )
        test_clock_in.shift_starts = self.starting_time - timedelta(minutes= 40)
        test_clock_in.save()
        new_periodic_task = PeriodicTask.objects.get(
            name=f"clock id = {test_clock_in.id}"
        )
        self.assertNotEqual(old_periodic_task, new_periodic_task)


class TestShiftActivation(TestCase):
    def setUp(self):
        self.starting_time = timezone.now()
        self.ending_time = timezone.now() + timedelta(minutes=40)
        self.weekday_setup = Weekday.objects.create(day=0)
        self.user = get_user_model().objects.create(
            email="normal@user.com", username="normal", password="foo",
            basic_hourly_wage=300
        )
        self.test_shift = Shift.objects.create(
            start_time=self.starting_time,
            end_time=self.ending_time,
            shift_weekday=self.weekday_setup,
            staff_on_shift=self.user
        )

    def test_shift_activation_just_in_time(self):
        """
        TC01: This clock in tests whether the system activates a shift if the user clocks in just in time
        """
        test_clock_in = ClockIn(
            shift=self.test_shift,
            shift_starts=self.starting_time,
            shift_ends=self.ending_time,
            status="CLSD"
        )
        self.assertFalse(test_clock_in.active, "clock in has not been saved so active is false")
        test_clock_in.save()
        self.assertTrue(test_clock_in.active, "clock in has been saved so active is now True")

    def test_shift_activation_just_before_clock_in_opening(self):
        """
        TC02: This tests whether the system activates a clock in if the clock in saved
        at the moment before the clock in time opens
        :return:
        """
        # if time is currently: 16:00, shift will now start at 16:41, which is 1 minute until
        # the clock in opens so active should be false
        starting_time = self.starting_time + timedelta(minutes=41)
        ending_time = starting_time + timedelta(minutes=40)
        test_clock_in = ClockIn.objects.create(
            shift=self.test_shift,
            shift_starts=starting_time,
            shift_ends=ending_time,
            status="CLSD"
        )
        self.assertFalse(test_clock_in.active)

    def test_shift_activation_just_after_clock_in_opening(self):
        """
        TCO03: This tests whether the system activates a clock in if the clock in saved just
        after the moment the clock in time opens
        :return:
        """
        # if the time is currently:16:00, shift will now start at 16:39, which is 1 minute past when
        # the clock in opens, so this be true
        starting_time = self.starting_time + timedelta(minutes=39)
        ending_time = starting_time + timedelta(minutes=40)
        test_clock_in = ClockIn.objects.create(
            shift=self.test_shift,
            shift_starts=starting_time,
            shift_ends=ending_time,
            status="CLSD"
        )
        self.assertTrue(test_clock_in.active)

    def test_shift_activation_just_after_shift_start_time(self):
        """
        TC04: This tests whether the system activates a clock in if the clock in saved in the minute just
        after the shift starts
        :return:
        """
        # if the time is currently 16:00, shift will now start at 15:59, which is 41 minutes after the clock in
        # opens
        starting_time = self.starting_time - timedelta(minutes=1)
        ending_time = starting_time + timedelta(minutes=40)
        test_clock_in = ClockIn.objects.create(
            shift=self.test_shift,
            shift_starts=starting_time,
            shift_ends=ending_time,
            status="CLSD"
        )
        self.assertTrue(test_clock_in.active)

    def test_shift_activation_much_before_shift_start_time(self):
        """
        TC05: This test whether the system activates after a clock in if the clock in saved many minutes
        before the shift starts
        :return:
        """
        # if the time is currently 16:00, shift will now start at 14:39 [which is within the 40 minutes buffer], but
        # not within the hourly buffer.
        starting_time = self.starting_time + timedelta(hours=1, minutes=39)
        ending_time = starting_time + timedelta(minutes=40)
        test_clock_in = ClockIn.objects.create(
            shift=self.test_shift,
            shift_starts=starting_time,
            shift_ends=ending_time,
            status="CLSD"
        )
        self.assertFalse(test_clock_in.active)


class TestDateShifting(TestCase):
    def setUp(self):
        self.starting_time = timezone.now()
        self.ending_time = timezone.now() + timedelta(minutes=40)
        self.weekday_setup = Weekday.objects.create(day=0)
        self.user = get_user_model().objects.create(
            email="normal@user.com", username="normal", password="foo",
            basic_hourly_wage=300
        )
        self.test_shift = Shift.objects.create(
            start_time=self.starting_time,
            end_time=self.ending_time,
            shift_weekday=self.weekday_setup,
            staff_on_shift=self.user
        )

        self.default_clock_in = ClockIn.objects.create(
            shift=self.test_shift,
            shift_starts=self.starting_time,
            shift_ends=self.ending_time,
            status="CLSD"
        )

    def test_shift_not_activated_on_no_clock_in(self):
        self.default_clock_in.on_shift = True
        self.default_clock_in.save()
        self.assertFalse(self.default_clock_in.active)

    def test_new_shift_creation(self):
        self.default_clock_in.on_shift = True
        self.default_clock_in.save()
        new_start_date, new_end_date = self.default_clock_in.shift_starts + timedelta(days=7), \
                                       self.default_clock_in.shift_ends + timedelta(days=7)
        next_clock_in = ClockIn.objects.get(
            shift=self.test_shift,
            shift_starts=new_start_date,
            shift_ends=new_end_date,
            status="CLSD"
        )
        self.assertIsNotNone(next_clock_in)