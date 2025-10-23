import re

from django.db import models
from django.conf import settings
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
