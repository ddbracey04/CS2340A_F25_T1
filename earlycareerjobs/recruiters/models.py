from django.db import models

class Recruiter(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='recruiter_images/')
    #price = models.IntegerField()
    def __str__(self):
        return str(self.id) + ' - ' + self.name