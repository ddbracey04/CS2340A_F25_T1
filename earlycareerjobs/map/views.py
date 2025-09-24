from django.shortcuts import render
from jobs.models import Job

# Create your views here.
def index(request):
    jobs = Job.objects.all()

    template_data = {}
    template_data['jobs'] = jobs
    return render(request, 'map/index.html', {'template_data': template_data})
