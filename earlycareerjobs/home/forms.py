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
            'work_style_preference',
        ]
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'github': forms.URLInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'work_style_preference': forms.Select(attrs={'class': 'form-control'}),
        }


class CandidateSearchForm(forms.Form):
    SORT_CHOICES = (
        ("recent", "Most recent"),
        ("name", "Name (A-Z)"),
        ("headline", "Headline (A-Z)"),
    )
    
    SKILLS_MODE_CHOICES = (
        ("AND", "Match ALL skills (AND)"),
        ("OR", "Match ANY skill (OR)"),
    )
    
    experience = forms.CharField(
        required=False,
        label="Experience",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Experience'
        })
    )
    
    skills_mode = forms.ChoiceField(
        required=False,
        label="Skills Match Mode",
        choices=SKILLS_MODE_CHOICES,
        initial="OR",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    location = forms.CharField(
        required=False,
        label="Location",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City, state, or country'
        })
    )
    
    distance = forms.IntegerField(
        required=False,
        label="Distance (miles)",
        initial=50,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Distance in miles',
            'min': '1'
        })
    )
    
    work_style = forms.ChoiceField(
        required=False,
        label="Work style preference",
        choices=[("", "Any work style")] + [(choice.value, choice.label) for choice in Profile.WorkStyle if choice.value],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    sort_by = forms.ChoiceField(
        required=False,
        label="Sort by",
        choices=SORT_CHOICES,
        initial="recent",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


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
