import re

from django.db import models
from users.models import CustomUser

# Create your models here.
class Job(models.Model):
    class WorkStyle(models.TextChoices):
        ANY    = "", ""
        REMOTE = "remote", "Remote"
        ONSITE = "onsite", "On-site"
        HYBRID = "hybrid", "Hybrid"

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, blank=True)
    skills = models.CharField(max_length=500, blank=True)  
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='job_images/', blank=True)
    date = models.DateTimeField(auto_now_add=True)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    users = models.ManyToManyField(CustomUser)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    work_style = models.CharField(
        max_length=10,
        choices=WorkStyle.choices,
        default=WorkStyle.ANY,
        blank=True
    )
    visa_sponsorship = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id) + ' - ' + self.title

    @property
    def skill_list(self):
        """Return normalized list of skills for template rendering."""
        if not self.skills:
            return []
        raw_tokens = re.split(r"(?:,|\n|;|\u2022|-)+", self.skills)
        return [skill.strip() for skill in raw_tokens if skill.strip()]


class Application(models.Model):
    STATUS_CHOICES = [
        ('APPLIED', 'Applied'),
        ('REVIEW', 'Under Review'),
        ('INTERVIEW', 'Interview'),
        ('OFFER', 'Offer'),
        ('CLOSED', 'Closed'),
    ]

    id = models.AutoField(primary_key=True)
    user_note = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='APPLIED')

    def __str__(self):
        return str(self.id) + ' - ' + self.job.title
