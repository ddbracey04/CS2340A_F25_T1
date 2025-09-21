from django.db import models
from django.contrib.auth.models import User

class Recruiter(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='recruiter_images/')
    #price = models.IntegerField()
    def __str__(self):
        return str(self.id) + ' - ' + self.name

class Application(models.Model):
    id = models.AutoField(primary_key=True)
    user_note = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + ' - ' + self.recruiter.name