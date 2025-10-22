from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        JOB_SEEKER = 'job_seeker', _('Job Seeker')
        RECRUITER = 'recruiter', _('Recruiter')
        ADMIN = 'admin', _('Administrator')
    
    id = models.AutoField(primary_key=True)

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
    
class ProfilePrivacy(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='privacy')
    
    # overall visibility
    is_profile_visible = models.BooleanField(default=True)
    
    # individual field visibility
    show_full_name = models.BooleanField(default=True)
    show_email = models.BooleanField(default=True)
    show_phone = models.BooleanField(default=False)
    show_location = models.BooleanField(default=True)
    show_resume = models.BooleanField(default=True)
    show_skills = models.BooleanField(default=True)
    show_experience = models.BooleanField(default=True)
    show_education = models.BooleanField(default=True)
    show_bio = models.BooleanField(default=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Privacy settings for {self.user.username}"
    
    class Meta:
        verbose_name_plural = "Profile privacy settings"