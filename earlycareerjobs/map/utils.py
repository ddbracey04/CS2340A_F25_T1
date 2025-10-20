from django.core.cache import cache
from geopy.geocoders import Nominatim
import time
import math

def lookupLatLon(cityName="", stateName="", countryName=""):
    # Initialize the Nominatim geocoder
    geolocator = Nominatim(user_agent="GATech_CS2340A_F25_T1")

    query = {}

    if cityName != "":
        query["city"] = cityName
    if stateName != "":
        query["state"] = stateName
    if countryName != "":
        query["country"] = countryName

    if len(query) == 0:
        print("Empty lat/lon lookup query")
        return 0, 0
    

    #Enforce 1 seconds between runs to abide by 1 call per second maximum
    rateLimitSecs = 1

    cacheKey = "Nominatum_Rate_Limit"
    prevTime = cache.get(cacheKey)
    
    # Block until rate limit is cleared
    currTime = time.time()
    while prevTime is not None and (currTime - prevTime) <= rateLimitSecs:
        currTime = time.time()



    # if prevTime is None or (currTime - prevTime) >= rateLimitSecs:
    #     # Update the cache with the current time
    #     cache.set(cacheKey, currTime, timeout=rateLimitSecs)
    # else:
    #     print("Could not execute map coordinate lookup due to being rate-limited to 1 request per second. Please try again.")
    #     return None, None
    
    # Perform geocoding
    # NOTE: Attribution already given to OpenStreetMaps on map
    location = geolocator.geocode(query)

    # Save time after geocode call to ensure proper rate limiting
    cache.set(cacheKey, time.time(), timeout=rateLimitSecs)
    
    if location:
        return location.latitude, location.longitude
    else:
        print(f"'{cityName}', '{stateName}', '{countryName}' not found.")
        return 0, 0
    
def haversine(lat_1, lon_1, lat_2, lon_2) -> float:
    r = 3959    # approximation of Earth's spherical radius, source: https://en.wikipedia.org/wiki/Earth_radius

    # Haversine distance formula, source: https://en.wikipedia.org/wiki/Haversine_formula
    d = 2 * r * math.asin(math.sqrt((1 - math.cos(lat_2 - lat_1) + (math.cos(lat_1) * math.cos(lat_2) * (1 - math.cos(lon_2 - lon_1)))) / 2))

    return d

