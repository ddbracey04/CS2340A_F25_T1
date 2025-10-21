import re

from django.db import models
from django.conf import settings

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='home_profile', related_query_name='home_profile',)
    headline = models.CharField(max_length=255, blank=True)
    skills = models.TextField(blank=True, help_text='Comma-separated skills')
    education = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    website = models.URLField(blank=True)
    
    # Location fields (optional)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def skill_list(self):
        """Return normalized list of skills for template rendering."""
        if not self.skills:
            return []
        raw_tokens = re.split(r"(?:,|\n|;|\u2022|-)+", self.skills)
        return [skill.strip() for skill in raw_tokens if skill.strip()]
