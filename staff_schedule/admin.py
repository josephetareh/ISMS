from django.contrib import admin

from staff_schedule.models import Event, EventType, Location, EventPersonnel, Weekday


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('location_name',)


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('type',)


# @admin.register(Weekday)
# class WeekdayAdmin(admin.ModelAdmin):
#     list_display = ("day",)


class EventPersonnelInline(admin.TabularInline):
    model = EventPersonnel


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'start_time', 'end_time', 'location')
    list_editable = ('start_time', 'end_time')
    inlines = [EventPersonnelInline]
