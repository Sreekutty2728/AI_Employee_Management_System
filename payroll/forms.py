from django import forms
from .models import Payroll


class PayrollForm(forms.ModelForm):

    class Meta:
        model = Payroll
        fields = [
            'employee',
            'month',
            'year',
            'basic_salary',
            'allowances',
            'deductions',
            'payment_date',
            'status',
        ]

        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-select'
            }),

            'month': forms.Select(attrs={
                'class': 'form-select'
            }),

            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 2026'
            }),

            'basic_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),

            'allowances': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),

            'deductions': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),

            'payment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),

            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
