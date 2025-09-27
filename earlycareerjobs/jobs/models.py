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
    description = models.TextField()
    image = models.ImageField(upload_to='job_images/')
    date = models.DateTimeField(auto_now_add=True)
    lat = models.FloatField()
    lon = models.FloatField()
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


class Application(models.Model):
    id = models.AutoField(primary_key=True)
    user_note = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + ' - ' + self.job.title