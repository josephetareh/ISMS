from django import forms
from django.forms import ModelForm, BaseModelFormSet, TextInput, Textarea, ClearableFileInput, NumberInput

from staff_schedule.models import Dispute, DisputeAttachment
from trainer.models import SessionExerciseItem


class DisputeFormSet(BaseModelFormSet):
    class Meta:
        fields = ("dispute_description",)


class DisputeForm(ModelForm):
    class Meta:
        model = Dispute
        fields = ("dispute_description",)

        widgets = {
            "dispute_description": Textarea(
                attrs={"class": "text-form py-6 px-6 extra-light zero-point-eight-seven-five-root w-100"}
            )
        }


class MyClearableFileInput(ClearableFileInput):
    initial_text = 'currently'
    input_text = 'change'
    clear_checkbox_label = 'clear'


class DisputeAttachmentForm(ModelForm):
    class Meta:
        model = DisputeAttachment
        fields = ("document",)

        widgets = {
            "document": ClearableFileInput(
                attrs={
                    "multiple": True,
                    "class": "success-text"
                }
            )
        }


class AddExerciseForm(ModelForm):

    class Meta:
        model = SessionExerciseItem
        fields = ("exercise_name", "sets", "reps")

        widgets = {
            "exercise_name": TextInput(
                attrs={
                    "class": "text-form py-4 px-7 col-6"
                }
            ),
            "sets": NumberInput(
                attrs={
                    "class": "py-4 px-7"
                }
            ),
            "reps": NumberInput(
                attrs={
                    "class": "py-4 px-7"
                }
            ),
        }

        labels = {
            "exercise_name": "Exercise Name"
        }



