from django.contrib import admin

from staff_schedule.models import Event, EventType, Location, EventPersonnel, Weekday, Shift, ClockIn, Dispute, \
    DisputeAttachment


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('location_name',)


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('type',)


@admin.register(Weekday)
class WeekdayAdmin(admin.ModelAdmin):
    list_display = ("day",)


class EventPersonnelInline(admin.TabularInline):
    model = EventPersonnel


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'location')
    # list_editable = ('start_time', 'end_time')
    inlines = [EventPersonnelInline]


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("staff_on_shift",)


@admin.register(ClockIn)
class ClockInAdmin(admin.ModelAdmin):
    list_display = ("shift", "time_clocked_in", "status")


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ("clock_in", "dispute_status")


@admin.register(DisputeAttachment)
class DisputeAttachmentAdmin(admin.ModelAdmin):
    list_display = ("dispute", "document")
