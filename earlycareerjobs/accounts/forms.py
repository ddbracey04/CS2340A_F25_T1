from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class RegForm(UserCreationForm):
    ROLE_OPTIONS = Profile.ROLE_OPTIONS

    firstName = forms.CharField(max_length = 50, label= 'First Name', required=True)
    lastName = forms.CharField(max_length = 50, label= 'Last Name', required=True)

    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_OPTIONS, widget=forms.RadioSelect, required=True)
    company = forms.CharField(max_length=250, required=False)

    class Meta:
        model = User
        fields = ("username", "firstName", "lastName", "email", "role", "company", "password1", "password2")
    
    # need to add method to verify company if role is recruiter

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["firstName"]
        user.last_name = self.cleaned_data["lastName"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data["role"]
            profile.company = self.cleaned_data.get("company")
            profile.save()
        return user