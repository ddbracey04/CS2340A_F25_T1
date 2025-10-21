import re

from django.db import models
from django.conf import settings

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='home_profile', related_query_name='home_profile',)
    headline = models.CharField(max_length=255, blank=True)
    skills = models.TextField(blank=True, help_text='Comma-separated skills')
    experience = models.TextField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    website = models.URLField(blank=True)

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
        ('BS', 'Bachelor\'s Degree'),
        ('MS', 'Master\'s Degree'),
        ('PhD', 'Doctorate'),
        ('OT', 'Other'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='educations')
    level = models.CharField(max_length=20, choices=PROFILE_EDUCATION_LEVELS)
    degree = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.get_level_display()}: {self.degree} from {self.institution}"