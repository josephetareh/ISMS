from django.contrib import admin

#
# # Register your models here.
# from trainer.models import ClientTrainerRelationship, Client, TrainerSession, SessionExerciseItem, SessionDetail
#
#
# class ExerciseListInline(admin.TabularInline):
#     model = SessionExerciseItem
#     show_change_link = True
#
#
# @admin.register(ClientTrainerRelationship)
# class TrainerClientRelationshipAdmin(admin.ModelAdmin):
#     list_display = ("trainer", "status", "total_paid")
#
#
# @admin.register(TrainerSession)
# class TrainerSessionAdmin(admin.ModelAdmin):
#     list_display = ("session_type", "trainer",)
#
#
# @admin.register(SessionDetail)
# class SessionDetailLogAdmin(admin.ModelAdmin):
#     list_display = ("session", "session_date")
#     inlines = [ExerciseListInline]
#
#
from trainer.models import Client, ClientTrainerRelationship, SessionExercises, SessionExerciseItem, TrainerSession, \
    GroupClass


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name")


@admin.register(ClientTrainerRelationship)
class TrainerClientRelationshipAdmin(admin.ModelAdmin):
    list_display = ("trainer", "client", "status", "total_paid")


@admin.register(SessionExerciseItem)
class ExerciseItemAdmin(admin.ModelAdmin):
    list_display = ("exercise_name", "sets", "reps")


class ExerciseListInline(admin.TabularInline):
    model = SessionExerciseItem
    show_change_link = True


# @admin.register(SessionExercises)
# class SessionDetailAdmin(admin.ModelAdmin):
#     list_display = ("session", "start_time", "end_time")


@admin.register(TrainerSession)
class TrainerSessionAdmin(admin.ModelAdmin):
    list_display = ("session_type", "trainer", "client", "sessions_left")


@admin.register(GroupClass)
class GroupClassAdmin(admin.ModelAdmin):
    list_display = ("class_name", "description", "trainer")
