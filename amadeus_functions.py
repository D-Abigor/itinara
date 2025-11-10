from dotenv import load_dotenv
import requests
import os
import time
import airportsdata

load_dotenv()

amadeusAPIKey = os.getenv("AMADEUSAPIKEY")
amadeusAPISecretKey = os.getenv("AMADEUSAPISECRET")
maxFlightAPIResults = 10
api_wait = 0.1

def getAirportCoords(IATA):
    airports = airportsdata.load('IATA')  # dictionary with IATA keys
    coords = airports[IATA]['lat'], airports[IATA]['lon']
    return coords

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
            amadeusAPIToken = refreshTOKEN(amadeusAPIKey, amadeusAPISecretKey)
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
    return [[datas["iataCode"], datas["geoCode"]] for datas in data["data"]][:2]
