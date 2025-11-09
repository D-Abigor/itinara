from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import requests
from pydantic import BaseModel
from geopy.distance import geodesic
import amadeus_functions as amadeus
from fastapi.middleware.cors import CORSMiddleware


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


def build_itinarary(details: journeydetail):
    src_coords = getLocationCoords(details.source)[::-1]    # fixing latitude longitude order
    dest_coords = getLocationCoords(details.destination)[::-1]    # fixing latitude longitude order
    #checking distance between A and B to apply constraints
    length = distance(src_coords,dest_coords)
    airways = []
    src_airports = amadeus.getNearestAirport(src_coords)
    dest_airports = amadeus.getNearestAirport(dest_coords)
    for src_airport in src_airports:
        for dest_airport in dest_airports:      # adding depart,arrive,flight number, cost, date, duration
            airways.append([flight["itineraries"] for flight in amadeus.flights(src_airport,dest_airport, details.date, details.time, details.travellers)["data"]])
    print(airways[0])   





            

            
        
    
    
    
    
    
    


