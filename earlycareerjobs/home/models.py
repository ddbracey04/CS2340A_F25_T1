from django.db import models


class Job(models.Model):
    class WorkStyle(models.TextChoices):
        REMOTE = "remote", "Remote"
        ONSITE = "onsite", "On-site"
        HYBRID = "hybrid", "Hybrid"

    title = models.CharField(max_length=200)
    skills = models.CharField(max_length=500, blank=True)  
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    work_style = models.CharField(
        max_length=10,
        choices=WorkStyle.choices,
        default=WorkStyle.ONSITE,
    )
    visa_sponsorship = models.BooleanField(default=False)

    def __str__(self):
        return self.title
