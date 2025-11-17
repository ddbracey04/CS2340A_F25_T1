import re

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser

class Profile(models.Model):
    class WorkStyle(models.TextChoices):
        ANY = "", "No preference"
        REMOTE = "remote", "Remote"
        ONSITE = "onsite", "On-site"
        HYBRID = "hybrid", "Hybrid"

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='home_profile', related_query_name='home_profile',)
    headline = models.CharField(max_length=255, blank=True)
    skills = models.TextField(blank=True, help_text='Comma-separated skills')
    experience = models.TextField(blank=True)

    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    website = models.URLField(blank=True)
    work_style_preference = models.CharField(
        max_length=10,
        choices=WorkStyle.choices,
        default=WorkStyle.ANY,
        blank=True,
        help_text='Preferred work environment for new roles',
    )

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def skill_list(self):
        """Return normalized list of skills for template rendering."""
        if not self.skills:
            return []
        raw_tokens = re.split(r"(?:,|\n|;|\u2022|-)+", self.skills)
        return [skill.strip() for skill in raw_tokens if skill.strip()]

class Education(models.Model):
    PROFILE_EDUCATION_LEVELS = [
        ('HS', 'High School'),
        ('AS', 'Associate Degree'),
        ('BS', "Bachelor's Degree"),
        ('MS', "Master's Degree"),
        ('PhD', 'Doctorate'),
        ('OT', 'Other'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='educations')
    level = models.CharField(max_length=20, choices=PROFILE_EDUCATION_LEVELS)
    degree = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.get_level_display()}: {self.degree} from {self.institution}"

class ProfilePrivacy(models.Model):
    # user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='privacy')
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='privacy')
    
    # overall visibility
    is_profile_visible = models.BooleanField(default=True)
    
    # individual field visibility    
    # show_full_name = models.BooleanField(default=True)
    # show_email = models.BooleanField(default=True)
    # show_phone = models.BooleanField(default=True)
    # show_resume = models.BooleanField(default=True)
    show_education = models.BooleanField(default=True)
    show_location = models.BooleanField(default=True)
    show_skills = models.BooleanField(default=True)
    show_experience = models.BooleanField(default=True)
    show_linkedin = models.BooleanField(default=True)
    show_github = models.BooleanField(default=True)
    show_website = models.BooleanField(default=True)
    show_work_style_preference = models.BooleanField(default=True)

    
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Privacy settings for {self.profile.user.username}"
    
    class Meta:
        verbose_name_plural = "Profile privacy settings"

class SavedSearch(models.Model):
    """
    Represents a search query saved by a recruiter.
    """
    recruiter = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='saved_candidate_searches',
        limit_choices_to={'role': CustomUser.Role.RECRUITER}
    )
    name = models.CharField(max_length=100, help_text="A name for this search, e.g., 'Senior Python Developers in SF'")
    
    # Search Parameters
    experience = models.CharField(max_length=255, blank=True)
    skills = models.TextField(blank=True, help_text="Comma-separated list of skills")
    skills_mode = models.CharField(max_length=3, default='OR', choices=[('OR', 'Match Any (OR)'), ('AND', 'Match All (AND)')])
    location = models.CharField(max_length=255, blank=True)
    distance = models.PositiveIntegerField(default=50, help_text="Search radius in miles")
    work_style = models.CharField(max_length=10, blank=True, choices=Profile.WorkStyle.choices)
    
    # Notification fields
    is_notification_active = models.BooleanField(default=True, help_text="Receive notifications for new candidates")
    last_checked = models.DateTimeField(null=True, blank=True, help_text="The last time we checked for new candidates")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def query_params(self):
        from urllib.parse import urlencode
        params = {
            'experience': self.experience,
            'skills_mode': self.skills_mode,
            'location': self.location,
            'distance': self.distance,
            'work_style': self.work_style,
        }
        # For skills, we need to create multiple 'skill' parameters
        if self.skills:
            # This is a simple approach. A more robust one would handle skills with commas.
            skill_list = [('skill', skill.strip()) for skill in self.skills.split(',') if skill.strip()]
            return urlencode(params) + '&' + urlencode(skill_list)
        return urlencode(params)

    def __str__(self):
        return f"'{self.name}' by {self.recruiter.username}"

    class Meta:
        ordering = ['-created_at']
        unique_together = ('recruiter', 'name')


class Notification(models.Model):
    """
    Represents a notification for a recruiter about new matching candidates.
    """
    recipient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    saved_search = models.ForeignKey(
        SavedSearch,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    candidate = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message[:50]}"


@receiver(post_save, sender=Profile)
def check_saved_searches_for_new_candidate(sender, instance, created, **kwargs):
    """
    When a profile is created or updated, check if it matches any saved searches
    and create notifications for recruiters.
    """
    from django.db.models import Q
    
    if not instance.user.is_job_seeker():
        return
    
    privacy, _ = ProfilePrivacy.objects.get_or_create(profile=instance)
    if not privacy.is_profile_visible:
        return
    
    active_searches = SavedSearch.objects.filter(is_notification_active=True)
    
    for search in active_searches:
        matches = True
        
        # Skills filter
        if search.skills:
            skills_list = [s.strip().lower() for s in search.skills.split(',') if s.strip()]
            if skills_list and instance.skills:
                profile_skills = [s.strip().lower() for s in instance.skills.split(',') if s.strip()]
                if search.skills_mode == 'AND':
                    matches = all(skill in ' '.join(profile_skills) for skill in skills_list)
                else:
                    matches = any(skill in ' '.join(profile_skills) for skill in skills_list)
            elif skills_list:
                matches = False
        
        # Experience filter
        if matches and search.experience:
            if not instance.experience or search.experience.lower() not in instance.experience.lower():
                matches = False
        
        # Work style filter
        if matches and search.work_style:
            if instance.work_style_preference != search.work_style:
                matches = False
        
        # If profile matches, create notification
        if matches:
            existing_notification = Notification.objects.filter(
                recipient=search.recruiter,
                saved_search=search,
                candidate=instance
            ).exists()
            
            if not existing_notification:
                Notification.objects.create(
                    recipient=search.recruiter,
                    saved_search=search,
                    candidate=instance,
                    message=f"New candidate '{instance.user.get_full_name() or instance.user.username}' matches your saved search '{search.name}'"
                )


class Message(models.Model):
    job = models.ForeignKey('jobs.Job', null=True, blank=True, on_delete=models.SET_NULL, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    text = models.TextField()
    in_app = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username} ({'in-app' if self.in_app else 'email'})"