import json
from geopy.distance import geodesic


def load_stations():
    with open('stations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    stations = []
    for feature in data.get("features", []):
        geom = feature.get("geometry")
        props = feature.get("properties", {})
        if geom and geom.get("type") == "Point":
            lon, lat = geom["coordinates"]
            stations.append({
                "code": props.get("code"),
                "name": props.get("name"),
                "state": props.get("state"),
                "lat": lat,
                "lon": lon
            })
    return stations


def load_trains():
    """Load train metadata (number, name, etc.)."""
    with open('trains.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    trains = {}
    for entry in data:
        trains[entry["train_number"]] = entry
    return trains


def load_schedules():
    """Load train schedules (routes)."""
    with open('shedules.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Some schedule files may be a FeatureCollection
    if isinstance(data, dict) and "features" in data:
        schedules = []
        for feature in data["features"]:
            props = feature.get("properties", {})
            schedules.append({
                "train_number": props.get("number"),
                "train_name": props.get("name"),
                "from_code": props.get("from_station_code"),
                "to_code": props.get("to_station_code"),
                "from_name": props.get("from_station_name"),
                "to_name": props.get("to_station_name"),
                "departure": props.get("departure"),
                "arrival": props.get("arrival"),
                "distance": props.get("distance")
            })
        return schedules
    else:
        return data


# -------------------------------
# Core Functions
# -------------------------------

def find_nearest_station(lat, lon, stations):
    """Find nearest station to a given coordinate."""
    nearest = min(
        stations,
        key=lambda s: geodesic((lat, lon), (s["lat"], s["lon"])).km
    )
    distance = geodesic((lat, lon), (nearest["lat"], nearest["lon"])).km
    return nearest, distance


def find_trains_between(src_code, dst_code, schedules):
    """Find trains that run directly between two station codes."""
    matches = []
    for s in schedules:
        if (
            (s["from_code"] == src_code and s["to_code"] == dst_code)
            or (s["from_code"] == dst_code and s["to_code"] == src_code)
        ):
            matches.append(s)
    return matches


def find_trains_between_points(source, destination):
    stations = load_stations()
    trains = load_trains()
    schedules = load_schedules()

    # Find nearest stations
    src_station, src_dist = find_nearest_station(source[0], source[1], stations)
    dst_station, dst_dist = find_nearest_station(destination[0], destination[1], stations)

    # Find matching trains between those stations
    connections = find_trains_between(src_station["code"], dst_station["code"], schedules)

    # Enrich with train info
    for c in connections:
        train_info = trains.get(c["train_number"])
        if train_info:
            c["train_name"] = train_info.get("train_name", c["train_name"])
            c["departure_time"] = train_info.get("departure", c["departure"])
            c["arrival_time"] = train_info.get("arrival", c["arrival"])

    return {
        "available_trains": connections
    }