from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import requests
from pydantic import BaseModel
import json
from dotenv import load_dotenv
import os
from geopy.distance import geodesic
import time

load_dotenv()

app = FastAPI()


amadeusAPIKey = os.getenv("AMADEUSAPIKEY")
amadeusAPISecretKey = os.getenv("AMADEUSAPISECRET")
photon_result_limit = 2
maxFlightAPIResults = 10
api_wait = 0.1







#--------------------------------------API Data Classes-----------------------------#

class journeydetail(BaseModel):
    source: str
    destination: str
    date: str
    time: str 
    travellers: str

#dummy values for testing
'''data = journeydetail(
    source="Vandipetta Road",
    destination="Thapar Institute of Engineering and Technology",
    date="2025-11-20",
    time="08:00",
    travellers="1"
)'''
    

#--------------------------------------API ENDPOINTS--------------------------------#

app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

@app.post("/detours")
async def getDetourLocs(request: Request):
    data = await request.json()

@app.post("/weather-advice")
async def getWeatherAdvice(request: Request):
    data = await request.json()

@app.post("/journey")
async def initializeItinarary(request: journeydetail):
    return build_itinarary(request)

@app.post("/autocomplete")
async def autoComplete(searchterm):
    api = "https://photon.komoot.io/api/?q=" + searchterm + "&limit=" + str(photon_result_limit)
    response = requests.get(api)
    data = response.json()
    return [results["properties"]["name"] for results in data["features"]]


#--------------------helper functions----------------------#

def getLocationCoords(location):
    api = "https://photon.komoot.io/api/?q=" + location + "&limit=1"
    response = requests.get(api)
    response = response.json()
    return response["features"][0]["geometry"]["coordinates"]

    

#def getNearestTrain(location):

def distance(src,dst):
    return int(geodesic(src,dst).km)

    





#----------------------AMADEOUS API FUNCTIONS----------------------#


def refreshTOKEN(key,secret):

    url = "https://test.api.amadeus.com/v1/security/oauth2/token"

    header = {
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    payload = {
     "grant_type": "client_credentials",
     "client_id": key,
     "client_secret": secret
    }

    response = requests.post(url, headers=header, data=payload)
    data = response.json()
    return data["access_token"]

amadeusAPIToken = refreshTOKEN(amadeusAPIKey, amadeusAPISecretKey)          ############

def flights(source,destination, date, Time, travellers):
    global amadeusAPIToken
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    time.sleep(api_wait)
    header = {
    "Authorization": f"Bearer {amadeusAPIToken}",
    "Content-Type": "application/json"
}


    payload = {
  "currencyCode": "INR",
  "originDestinations": [
    {
      "id": "1",
      "originLocationCode": source,
      "destinationLocationCode": destination,
      "departureDateTimeRange": {
        "date": date,
        "time": Time
      }
    }
  ],
  "travelers": [
    {
      "id": travellers,
      "travelerType": "ADULT"
    }
  ],
  "sources": [
    "GDS"
  ],
  "searchCriteria": {
    "maxFlightOffers": maxFlightAPIResults,
    "flightFilters": {
      "cabinRestrictions": [
        {
          "cabin": "ECONOMY",
          "coverage": "MOST_SEGMENTS",
          "originDestinationIds": [
            "1"
          ]
        }
      ]
    }
  }
}
    
    
    
    response = requests.post(url, headers=header, json=payload)
    data = response.json()
    if "errors" in data:
        if data["errors"][-1] == 401:             # handling token expiry
            amadeusAPIToken = refreshTOKEN()
            response = requests.get(url, headers=header, json=payload)
            data = response.json()
    return data



def getNearestAirport(location):            # location as  [lat,long]
    time.sleep(api_wait)
    url = f"https://test.api.amadeus.com/v1/reference-data/locations/airports?latitude={location[0]}&longitude={location[1]}&radius=500&page%5Blimit%5D=10&page%5Boffset%5D=0&sort=relevance"
 
    header = {
    "Authorization": f"Bearer {amadeusAPIToken}",
    "accept": "application/vnd.amadeus+json"
    }

    response = requests.get(url, headers=header)
    data = response.json()
    return [datas["iataCode"] for datas in data["data"]][:2]


def build_itinarary(details: journeydetail):
    src_coords = getLocationCoords(details.source)[::-1]    # fixing latitude longitude order
    dest_coords = getLocationCoords(details.destination)[::-1]    # fixing latitude longitude order
    #checking distance between A and B to apply constraints
    length = distance(src_coords,dest_coords)
    airways = []
    src_airports = getNearestAirport(src_coords)
    dest_airports = getNearestAirport(dest_coords)
    print(src_airports, dest_airports)
    for src_airport in src_airports:
        for dest_airport in dest_airports:
            airways.append(flights(src_airport,dest_airport, details.date, details.time, details.travellers))
    




            

            
        
    
    
    
    
    
    






