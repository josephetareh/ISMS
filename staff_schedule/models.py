from django.conf import settings
from django.db import models


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


class Event(models.Model):
    event_name = models.CharField(max_length=300, blank=False)
    description = models.TextField(max_length=1000, blank=True, null=True)
    type = models.ForeignKey(EventType, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    staff_working = models.ManyToManyField(settings.AUTH_USER_MODEL, through="EventPersonnel",
                                           through_fields=('event', 'staff_on_event'))

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

