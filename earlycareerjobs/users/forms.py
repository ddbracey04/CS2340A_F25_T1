from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, ProfilePrivacy

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[(role, label) for role, label in CustomUser.Role.choices if role != CustomUser.Role.ADMIN],
        widget=forms.RadioSelect,
        initial=CustomUser.Role.JOB_SEEKER
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Force email field error messages to English
        self.fields['email'].error_messages = {
            'invalid': 'Enter a valid email address.',
            'required': 'This field is required.',
        }
        if 'role' in self.data:
            role = self.data.get('role')
            if role == CustomUser.Role.RECRUITER:
                self.fields['company_name'] = forms.CharField(max_length=100)
        # Do not add resume field at registration


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