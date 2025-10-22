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
        ("name", "Name (A–Z)"),
        ("headline", "Headline (A–Z)"),
    )

    keywords = forms.CharField(
        required=False,
        label="Keywords",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Skills, names, or experience'
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
