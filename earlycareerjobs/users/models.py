from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        JOB_SEEKER = 'job_seeker', _('Job Seeker')
        RECRUITER = 'recruiter', _('Recruiter')
        ADMIN = 'admin', _('Administrator')
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.JOB_SEEKER
    )
    
    phone_number = models.CharField(max_length=15, blank=True)
    company_name = models.CharField(max_length=100, blank=True)  # for recruiters
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)  # for job seekers
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        # If user is superuser, always set role to ADMIN
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    def is_job_seeker(self):
        return self.role == self.Role.JOB_SEEKER

    def is_recruiter(self):
        return self.role == self.Role.RECRUITER

    def is_admin(self):
        return self.role == self.Role.ADMIN