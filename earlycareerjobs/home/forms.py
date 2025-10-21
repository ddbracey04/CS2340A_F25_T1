from django import forms
from .models import Profile
from .models import Education

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'headline',
            'skills',
            'experience',
            'city',
            'state',
            'country',
            'linkedin',
            'github',
            'website',
        ]
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'github': forms.URLInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = [
            'level',
            'degree',
            'institution'
        ]
        widgets = {
            'level': forms.Select(attrs={'class': 'form-control'}),
            'degree': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Computer Science'}),
            'institution': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Georgia Institute of Technology'}),
        }