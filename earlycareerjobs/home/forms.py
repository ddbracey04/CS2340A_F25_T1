from django import forms
from .models import Profile, Education, ProfilePrivacy, SavedSearch

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


class ProfileHeadlineForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['headline']
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write a short professional headline'})
        }


class ProfileLocationForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['city', 'state', 'country']
        widgets = {
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
        }


class ProfileSkillsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['skills']
        widgets = {
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Comma-separated skills'})
        }


class ProfileWorkStyleForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['work_style_preference']
        widgets = {
            'work_style_preference': forms.Select(attrs={'class': 'form-select'})
        }


class ProfileExperienceForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['experience']
        widgets = {
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Highlight your experience...'})
        }


class ProfileLinksForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['linkedin', 'github', 'website']
        widgets = {
            'linkedin': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'LinkedIn URL'}),
            'github': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'GitHub URL'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Personal website URL'}),
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

class PrivacySettingsForm(forms.ModelForm):
    class Meta:
        model = ProfilePrivacy
        fields = [
            'is_profile_visible',
            # 'show_full_name',
            # 'show_email', 
            # 'show_phone',
            # 'show_resume',
            'show_education',
            'show_location',
            'show_skills',
            'show_experience',
            'show_linkedin',
            'show_github',
            'show_website',
            'show_work_style_preference',
        ]
        
        labels = {
            'is_profile_visible': 'Make my profile visible to recruiters',
            # 'show_full_name': 'Full Name',
            # 'show_email': 'Email Address',
            # 'show_phone': 'Phone',
            # 'show_resume': 'Resume',
            'show_education': 'Education',
            'show_location': 'Location',
            'show_skills': 'Skills',
            'show_experience': 'Experience',
            'show_linkedin': 'LinkedIn',
            'show_github': 'GitHub',
            'show_website': 'Personal Website',
            'show_work_style_preference': 'Work Style Preference',
        }


class MessageForm(forms.Form):
    recipient_username = forms.CharField(
        required=True,
        label="Recipient username",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Candidate username'})
    )

    job_id = forms.IntegerField(
        required=False,
        label="Job (optional)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Optional job id'})
    )

    message_text = forms.CharField(
        required=True,
        label="Message",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Write your message here...'})
    )

    SEND_METHOD_CHOICES = (
        ("in_app", "Message in App"),
        ("email", "Email Candidate"),
    )

    send_method = forms.ChoiceField(
        required=True,
        label="Send method",
        choices=SEND_METHOD_CHOICES,
        initial="in_app",
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
        
    widgets = {            
        'is_profile_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        # 'show_full_name': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        # 'show_email',: forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        # 'show_phone': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        # 'show_resume': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        'show_education': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        'show_location': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        'show_skills': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        'show_experience': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        'show_linkedin': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        'show_github': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        'show_website': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        'show_work_style_preference': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }


class SavedSearchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['is_notification_active'].widget.attrs.update({'class': 'form-check-input'})

    class Meta:
        model = SavedSearch
        fields = ['name', 'experience', 'skills', 'skills_mode', 'location', 'distance', 'work_style', 'is_notification_active']
        widgets = {
            'experience': forms.HiddenInput(),
            'skills': forms.HiddenInput(),
            'skills_mode': forms.HiddenInput(),
            'location': forms.HiddenInput(),
            'distance': forms.HiddenInput(),
            'work_style': forms.HiddenInput(),
        }
