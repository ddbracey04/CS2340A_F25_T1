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


def index(request, errorStr='', override_template_data=None):

    if (override_template_data != None):
        override_template_data['jobs'] = Job.objects.filter(id__in=override_template_data['jobIds'])

        return render(request, 'map/index.html', {'template_data': override_template_data, 'error': errorStr})

    jobs = Job.objects.all()

    template_data = {}
    template_data['jobs'] = jobs

    if (request.user.is_authenticated):
        DEFAULT_SEARCH_RADIUS = 5
        template_data['searchRadius'] = DEFAULT_SEARCH_RADIUS

        if (request.user.city and request.user.city != ''):
            template_data['searchCity'] = request.user.city

        if (request.user.state and request.user.state != ''):
            template_data['searchState'] = request.user.state

        if (request.user.country and request.user.country != ''):
            template_data['searchCountry'] = request.user.country

        if (request.user.lat and request.user.lat != ''):
            template_data['centerLat'] = request.user.lat

        if (request.user.lon and request.user.lon != ''):
            template_data['centerLon'] = request.user.lon

    return render(request, 'map/index.html', {'template_data': template_data, 'error': errorStr})

def filter(request):
    if request.method == "POST":
        searchCity = request.POST["city_filter"]
        searchState = request.POST["state_filter"]
        searchCountry = request.POST["country_filter"]

        if searchCity == '' and searchState == '' and searchCountry == '':
            old_template_data = {}
            old_template_data['searchCity'] = request.POST['old_city']
            old_template_data['searchState'] = request.POST['old_state']
            old_template_data['searchCountry'] = request.POST['old_country']
            old_template_data['searchRadius'] = request.POST['old_radius']
            old_template_data['centerLat'] = request.POST['old_lat']
            old_template_data['centerLon'] = request.POST['old_lon']
            old_template_data['jobIds'] = request.POST.getlist('old_job_id[]')
            return index(request, "No Filter Location Provided", old_template_data)
            template_data = {}
            template_data['jobs'] = Job.objects.all()
            return render(request, 'map/index.html', {'template_data': template_data})


        searchLat, searchLon = lookupLatLon(searchCity, searchState, searchCountry)

        if searchLat == 0 and searchLon == 0:
            old_template_data = {}
            old_template_data['searchCity'] = request.POST['old_city']
            old_template_data['searchState'] = request.POST['old_state']
            old_template_data['searchCountry'] = request.POST['old_country']
            old_template_data['searchRadius'] = request.POST['old_radius']
            old_template_data['centerLat'] = request.POST['old_lat']
            old_template_data['centerLon'] = request.POST['old_lon']
            old_template_data['jobIds'] = request.POST.getlist('old_job_id[]')
            return index(request, f"Could not find {request.POST['city_filter']}, {request.POST['state_filter']}, {request.POST['country_filter']}", old_template_data)
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
        old_template_data = {}
        old_template_data['searchCity'] = request.POST['old_city']
        old_template_data['searchState'] = request.POST['old_state']
        old_template_data['searchCountry'] = request.POST['old_country']
        old_template_data['searchRadius'] = request.POST['old_radius']
        old_template_data['centerLat'] = request.POST['old_lat']
        old_template_data['centerLon'] = request.POST['old_lon']
        old_template_data['jobIds'] = request.POST.getlist('old_job_id[]')
        return render(request, 'map/index.html', {'template_data': old_template_data})


