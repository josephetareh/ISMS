from django import forms
from django.forms import ModelForm, BaseModelFormSet, TextInput, Textarea, ClearableFileInput

from staff_schedule.models import Dispute, DisputeAttachment


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
        fields = ("document", )

        widgets = {
            "document": ClearableFileInput(
                attrs={
                    "multiple": True,
                    "class": "success-text"
                }
            )
        }