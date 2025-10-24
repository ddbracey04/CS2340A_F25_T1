from django import forms
from .models import Profile, Education, ProfilePrivacy

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

class PrivacySettingsForm(forms.ModelForm):
    class Meta:
        model = ProfilePrivacy
        fields = [
            'is_profile_visible',
            'show_full_name',
            'show_email', 
            'show_phone',
            'show_location',
            'show_resume',
            'show_skills',
            'show_experience',
            'show_education',
            'show_bio'
        ]
        
        labels = {
            'is_profile_visible': 'Make my profile visible to recruiters',
            'show_full_name': 'Full Name',
            'show_email': 'Email Address',
            'show_phone': 'Phone Number',
            'show_location': 'Location',
            'show_resume': 'Resume/CV',
            'show_skills': 'Skills',
            'show_experience': 'Years of Experience',
            'show_education': 'Education',
            'show_bio': 'Bio/Summary'
        }
        
        widgets = {
            'is_profile_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_full_name': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_phone': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_location': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_resume': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_skills': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_experience': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_education': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_bio': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
