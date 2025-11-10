from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import requests
from pydantic import BaseModel
from geopy.distance import geodesic
import amadeus_functions as amadeus
from fastapi.middleware.cors import CORSMiddleware
import train_functions

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

photon_result_limit = 3
#--------------------------------------API Data Classes-----------------------------#

class journeydetail(BaseModel):
    source: str
    destination: str
    date: str
    time: str 
    travellers: str
    
#--------------------------------------API ENDPOINTS--------------------------------#
@app.post("/detours")
async def getDetourLocs(request: Request):
    data = await request.json()

@app.post("/weather-advice")
async def getWeatherAdvice(request: Request):
    data = await request.json()

@app.post("/journey")
async def initializeItinarary(request: journeydetail):
    return build_itinarary(request)

@app.get("/autocomplete")
def autoComplete(searchterm: str):
    api = "https://photon.komoot.io/api/?q=" + searchterm + "&limit=" + str(photon_result_limit)
    response = requests.get(api)
    data = response.json()
    return [results["properties"]["name"] for results in data["features"]]

app.mount("/", StaticFiles(directory="frontend/", html=True), name="landing")


#--------------------helper functions----------------------#

def getLocationCoords(location):
    api = "https://photon.komoot.io/api/?q=" + location + "&limit=1"
    response = requests.get(api)
    response = response.json()
    return response["features"][0]["geometry"]["coordinates"]

    

#def getNearestTrain(location):

def distance(src,dst):
    return int(geodesic(src,dst).km)


def build_itinarary(details: journeydetail):
    src_coords = getLocationCoords(details.source)[::-1]    # fixing latitude longitude order
    dest_coords = getLocationCoords(details.destination)[::-1]    # fixing latitude longitude order
    #checking distance between A and B to apply constraints
    length = int(distance(src_coords,dest_coords))
    if length>800:
        UID = 0
        airways = {}
        src_airports = amadeus.getNearestAirport(src_coords)
        dest_airports = amadeus.getNearestAirport(dest_coords)
        for src_airport in src_airports:                # src_airports --> [iatia code, geocode]        #geocode = {'langitude': xxxx, 'longitude':xxxx}
            for dest_airport in dest_airports:      # adding depart,arrive,flight number, cost, date, duration
                flights = amadeus.flights(src_airport[0],dest_airport[0], details.date, details.time, details.travellers)
                offers = flights['data']
                for offer in offers:
                    price = offer['price']['total']
                    for itinerary in offer['itineraries']:
                        UID+=1
                        temp_pack = []
                        for seg in itinerary['segments']:
                            dep_airport = seg['departure']['iataCode']
                            dep_time = seg['departure']['at']
                            arr_airport = seg['arrival']['iataCode']
                            arr_time = seg['arrival']['at']
                            flight_no = seg['carrierCode'] + seg['number']
                            temp_pack.append([dep_airport, dep_time, arr_airport, arr_time, flight_no ])
                        temp_pack.append(price)
                        airways[UID] = temp_pack
    print(train_functions.find_trains_between_points(amadeus.getAirportCoords(dest_airports[0]), dest_coords))
        




            

            
        
    
    
    
    
    
    


