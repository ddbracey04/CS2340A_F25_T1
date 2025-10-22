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
    
def reverseLocationLookup(lat: float, lon: float):
    lat = float(lat)
    lon = float(lon)
    # Initialize the Nominatim geocoder
    geolocator = Nominatim(user_agent="GATech_CS2340A_F25_T1")

    if lat < -90 or lat > 90 or lon < -180 or lon > 180:
        print(f'Invalid Lat/Long: {lat} lat, {lon} long')
        return "", "", ""
    
    query = (lat, lon) 

    #Enforce 1 seconds between runs to abide by 1 call per second maximum
    rateLimitSecs = 1

    cacheKey = "Nominatum_Rate_Limit"
    prevTime = cache.get(cacheKey)
    
    # Block until rate limit is cleared
    currTime = time.time()
    while prevTime is not None and (currTime - prevTime) <= rateLimitSecs:
        currTime = time.time()
    
    # Perform reverse geocoding up to city level
    # NOTE: Attribution already given to OpenStreetMaps on map
    location = geolocator.reverse(query, zoom=13)

    # Save time after geocode call to ensure proper rate limiting
    cache.set(cacheKey, time.time(), timeout=rateLimitSecs)
    
    if location:
        addressDict = location.raw["address"]
        if "city" in addressDict:
            city = addressDict["city"]
        elif "town" in addressDict:
            city = addressDict["town"]
        elif "borough" in addressDict:
            city = addressDict["borough"]
        elif "village" in addressDict:
            city = addressDict["village"]
        elif "suburb" in addressDict:
            city = addressDict["suburb"]
        else:
            city = ""

        if "state" in addressDict:
            state = addressDict["state"]
        else:
            state = ""
        
        if "country" in addressDict:
            country = addressDict["country"]
        else:
            country = ""
        
        return city, state, country
    else:
        print(f'Error Reverse Searching Lat/Long: {lat} lat, {lon} long')
        return "", "", ""
    
def haversine(lat_1, lon_1, lat_2, lon_2) -> float:
    # Adapted from: https://www.geeksforgeeks.org/dsa/haversine-formula-to-find-distance-between-two-points-on-a-sphere/
    dLat = (lat_2 - lat_1) * math.pi / 180.0
    dLon = (lon_2 - lon_1) * math.pi / 180.0

    lat_1 = (lat_1) * math.pi / 180.0
    lat_2 = (lat_2) * math.pi / 180.0

    a = (math.sin(dLat / 2) * math.sin(dLat / 2)) + (math.sin(dLon / 2) * math.sin(dLon / 2)) * math.cos(lat_1) * math.cos(lat_2)
    rad = 3959
    c = 2 * math.asin(math.sqrt(a))
    return rad * c

