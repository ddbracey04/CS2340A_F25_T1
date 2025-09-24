from django.shortcuts import render, redirect
from jobs.models import Job

# Create your views here.
def select_location(request):
    if request.method == "POST":
        job = Job.objects.get(id=request.POST["jobId"])
        job.lat = request.POST["lat"]
        job.lon = request.POST["lon"]
        job.save()
    
    return redirect('map.index')


def index(request):
    jobs = Job.objects.all()

    template_data = {}
    template_data['jobs'] = jobs
    return render(request, 'map/index.html', {'template_data': template_data})
