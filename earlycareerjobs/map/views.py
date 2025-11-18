from django.shortcuts import render, redirect
from jobs.models import Job
from .utils import lookupLatLon, reverseLocationLookup, haversine
from home.models import Profile
from django.core.exceptions import ObjectDoesNotExist
from users.models import CustomUser

# import numpy as np
# from scipy.cluster.hierarchy import linkage, fcluster
# from scipy.spatial.distance import squareform

# Create your views here.
def select_location(request):
    if request.method == "POST":
        job = Job.objects.get(id=request.POST["jobId"])
        job.lat = request.POST["lat"]
        job.lon = request.POST["lon"]
        _, job.city, job.state, job.country = reverseLocationLookup(request.POST["lat"], request.POST["lon"])
        job.save()

        return redirect('map.indexLatLon', lat=request.POST["lat"], lon=request.POST["lon"])
    
    return redirect('map.index')


def index(request, errorStr='', override_template_data=None, focusLat="", focusLon="", useFilter=True):

    if (override_template_data != None):
        override_template_data['jobs'] = Job.objects.filter(id__in=override_template_data['jobIds'])

        return render(request, 'map/index.html', {'template_data': override_template_data, 'error': errorStr})

    jobs = Job.objects.all()

    template_data = {}
    template_data['jobs'] = jobs

    if request.user.is_authenticated: # and hasattr(request.user, "profile"):
        try:
            profile = Profile.objects.get(user=request.user)
            print("HAS PROFILE")

            if (profile.lat and profile.lat != ''):
                template_data['centerLat'] = profile.lat

            if (profile.lon and profile.lon != ''):
                template_data['centerLon'] = profile.lon

            if useFilter:
                
                if (profile.commute_radius and profile.commute_radius > 0):
                    template_data['searchRadius'] = profile.commute_radius
                else:
                    DEFAULT_SEARCH_RADIUS = 5
                    template_data['searchRadius'] = DEFAULT_SEARCH_RADIUS

                if (profile.city and profile.city != ''):
                    template_data['searchCity'] = profile.city

                if (profile.state and profile.state != ''):
                    template_data['searchState'] = profile.state

                if (profile.country and profile.country != ''):
                    template_data['searchCountry'] = profile.country

                if (profile.city != '' or profile.state != '' or profile.country != '') and profile.lat == 0 and profile.lon == 0:
                    errorStr = f"Could not find {profile.city}, {profile.state}, {profile.country}"

                if ('centerLat' in template_data and 'centerLon' in template_data):
                    filteredJobs = []
                    for job in jobs:
                        if haversine(float(profile.lat), float(profile.lon), float(job.lat), float(job.lon)) < float(DEFAULT_SEARCH_RADIUS):
                            filteredJobs += [job]

                    template_data['jobs'] = filteredJobs

        except ObjectDoesNotExist:
            # Do nothing if profile does not exist yet
            # TODO: Figure out what we want to do here
            pass
    
    if focusLat != "" and focusLon != "":
        template_data['centerLat'] = float(focusLat)
        template_data['centerLon'] = float(focusLon)
        template_data['searchRadius'] = ''

    if request.user.is_authenticated:
        if request.user.is_recruiter() or request.user.is_admin():
            all_profiles = list(Profile.objects.filter(user__role=CustomUser.Role.JOB_SEEKER))
            template_data["profiles"] = all_profiles
            # dist_map = np.array([[0 for _ in range(len(all_profiles))] for _ in range(len(all_profiles))])
            # print(dist_map)
            # for i in range(len(all_profiles)):
            #     for j in range(len(all_profiles) - i - 1):
            #         j += i + 1
            #         print(i, ", ", j)
            #         dist = haversine(all_profiles[i].lat, all_profiles[i].lon, all_profiles[j].lat, all_profiles[j].lon)
            #         dist_map[i][j] = dist
            #         dist_map[j][i] = dist

            # print(dist_map)

            # # Convert square distance matrix to condensed form
            # condensed_dist = squareform(dist_map)

            # # Perform hierarchical clustering (average linkage)
            # Z = linkage(condensed_dist, method='average')

            # # Assign cluster labels (e.g., 2 clusters)
            # labels = fcluster(Z, t=1, criterion='maxclust')

            # print("Cluster labels:", labels)

            # print(list(all_profiles))
            # print(list(all_profiles)[0].lat)

    return render(request, 'map/index.html', {'template_data': template_data, 'error': errorStr})

def indexLatLon(request, lat, lon):
    return index(request=request, focusLat=lat, focusLon=lon)

def indexNoFilter(request):
    return index(request=request, useFilter=False)

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


        searchLat, searchLon = lookupLatLon(cityName=searchCity, stateName=searchState, countryName=searchCountry)

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


