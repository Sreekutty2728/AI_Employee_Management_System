from django import forms
from .models import Department


class DepartmentForm(forms.ModelForm):

    class Meta:
        model = Department

        fields = [
            'department_name',
            'department_code',
            'department_head',
            'description',
            'status',
        ]

        widgets = {
            'department_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Department Name'
            }),

            'department_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Department Code'
            }),

            'department_head': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Department Head'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter Department Description'
            }),

            'status': forms.Select(
                choices=[
                    ('Active', 'Active'),
                    ('Inactive', 'Inactive')
                ],
                attrs={
                    'class': 'form-control'
                }
            ),
        }