from django.core.cache import cache
from geopy.geocoders import Nominatim
import time

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
        return None, None
    

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
        return None, None