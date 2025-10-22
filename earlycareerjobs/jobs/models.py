from django.db import models
from users.models import CustomUser

# Create your models here.
class Job(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='job_images/')
    date = models.DateTimeField(auto_now_add=True)
    lat = models.FloatField(default=0.0)
    lon = models.FloatField(default=0.0)
    users = models.ManyToManyField(CustomUser)
    
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