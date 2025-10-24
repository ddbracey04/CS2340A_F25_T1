from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

# Form for recruiter to search candidates
class CandidateSearchForm(forms.Form):
    skills = forms.CharField(
        required=False,
        label='Skills',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Python, Excel', 'class': 'form-control'})
    )
    location = forms.CharField(
        required=False,
        label='Location',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Atlanta', 'class': 'form-control'})
    )
    projects = forms.CharField(
        required=False,
        label='Projects',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Web App', 'class': 'form-control'})
    )

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[(role, label) for role, label in CustomUser.Role.choices if role != CustomUser.Role.ADMIN],
        widget=forms.RadioSelect(attrs={'id': 'id_role'}),
        initial=CustomUser.Role.JOB_SEEKER
    )
    company_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_company_name'})
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].error_messages = {
            'invalid': 'Enter a valid email address.',
            'required': 'This field is required.',
        }
        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            if field_name != 'role':
                field.widget.attrs['class'] = 'form-control'
    
    def clean_company_name(self):
        role = self.cleaned_data.get('role')
        company_name = self.cleaned_data.get('company_name')
        
        if role == CustomUser.Role.RECRUITER and not company_name:
            raise forms.ValidationError('Company name is required for recruiters.')
        
        return company_name