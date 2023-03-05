from django.contrib import admin

from staff_schedule.models import Event, EventType, Location, EventPersonnel, Weekday, Shift, ClockIn, Dispute, \
    DisputeAttachment, ISMSSchedule, GroupClass, Meeting, GroupClassPayment


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


@admin.register(ISMSSchedule)
class ISMSScheduleAdmin(admin.ModelAdmin):
    list_display = ('schedule_type', 'schedule_day', 'start_time', 'end_time')


@admin.register(GroupClass)
class GroupClassAdmin(admin.ModelAdmin):
    list_display = ('class_name', "trainer")


@admin.register(GroupClassPayment)
class GroupClassPaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_for_class", "attendees", "total_payment")


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('meeting_title',)


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
