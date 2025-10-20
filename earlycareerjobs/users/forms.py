from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[(role, label) for role, label in CustomUser.Role.choices if role != CustomUser.Role.ADMIN],
        widget=forms.RadioSelect,
        initial=CustomUser.Role.JOB_SEEKER
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'city', 'state', 'country', 'password1', 'password2')
    
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