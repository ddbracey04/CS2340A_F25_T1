from django import forms
from .models import JobApplication
from django.forms import ModelForm

class JobApplicationForm(ModelForm):
    class Meta:
        model = JobApplication
        fields = ['company', 'position', 'status', 'notes']

class StatusUpdateForm(ModelForm):
    class Meta:
        model = JobApplication
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'border border-gray-300 rounded px-3 py-1 text-sm focus:outline-none focus:border-gray-500'
            })
        }