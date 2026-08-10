from django import forms
from .models import LeaveRequest


class LeaveRequestForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is not None and not user.is_staff:
            self.fields.pop('employee', None)



    class Meta:
        model = LeaveRequest
        fields = [
            'employee',
            'leave_type',
            'start_date',
            'end_date',
            'reason',
        ]

        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-select'
            }),

            'leave_type': forms.Select(attrs={
                'class': 'form-select'
            }),

            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),

            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),

            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter leave reason'
            }),
        }
