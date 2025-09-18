from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.
class Profile(models.Model):
    ROLE_OPTIONS = (
        ('job_seeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
    )
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_OPTIONS, default='job_seeker')
    company = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'
    
@receiver(post_save, sender='auth.User')
def create_or_update_user_profile(sender, instance, created, **kwargs):
    # if created:
    #     Profile.objects.create(user=instance)
    # else:
    #     instance.profile.save()
    profile, created_profile = Profile.objects.get_or_create(user=instance)
    if not created_profile:
        profile.save()