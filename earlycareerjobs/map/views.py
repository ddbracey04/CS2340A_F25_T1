from django.shortcuts import render, redirect
from jobs.models import Job
from .utils import lookupLatLon, haversine

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

def filter(request):
    if request.method == "POST":
        searchCity = request.POST["city_filter"]
        searchState = request.POST["state_filter"]
        searchCountry = request.POST["country_filter"]

        if searchCity == '' and searchState == '' and searchCountry == '':
            template_data = {}
            template_data['jobs'] = Job.objects.all()
            return render(request, 'map/index.html', {'template_data': template_data})


        searchLat, searchLon = lookupLatLon(searchCity, searchState, searchCountry)

        if searchLat == 0 and searchLon == 0:
            template_data = {}
            template_data['jobs'] = Job.objects.all()
            return render(request, 'map/index.html', {'template_data': template_data})

        
        searchRadius = request.POST["radius_filter"]
        
        allJobs = Job.objects.all()
        filteredJobs = []

        for job in allJobs:
            if haversine(float(searchLat), float(searchLon), float(job.lat), float(job.lon)) < float(searchRadius):
                filteredJobs += [job]
    
        template_data = {}
        template_data['jobs'] = filteredJobs
        template_data['centerLat'] = searchLat
        template_data['centerLon'] = searchLon
        template_data['searchRadius'] = searchRadius
        template_data['searchCity'] = searchCity
        template_data['searchState'] = searchState
        template_data['searchCountry'] = searchCountry

        return render(request, 'map/index.html', {'template_data': template_data})
    else:
        template_data = {}
        template_data['jobs'] = Job.objects.all()
        return render(request, 'map/index.html', {'template_data': template_data})


