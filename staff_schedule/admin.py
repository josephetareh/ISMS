from django.contrib import admin

from staff_schedule.models import Weekday, Shift, ClockIn, Dispute, \
    DisputeAttachment, ISMSScheduleFixedEvent, Meeting, ISMSScheduleCalendarEvent, TrainingSessionInfo


@admin.register(Weekday)
class WeekdayAdmin(admin.ModelAdmin):
    list_display = ("day",)


class TrainingSessionInfoInline(admin.TabularInline):
    model = TrainingSessionInfo


@admin.register(ISMSScheduleFixedEvent)
class ISMSFixedScheduleAdmin(admin.ModelAdmin):
    list_display = ('schedule_type', 'schedule_day', 'start_time', 'end_time')


@admin.register(ISMSScheduleCalendarEvent)
class ISMSScheduleCalendarEventAdmin(admin.ModelAdmin):
    list_display = ("schedule_type",)
    inlines = [TrainingSessionInfoInline, ]


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
