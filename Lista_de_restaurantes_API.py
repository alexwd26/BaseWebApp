# Directory layout:
# .
# ├── app.py
# ├── services/
# │   └── osm_service.py
# └── requirements.txt

# === File: app.py ===
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.osm_service import get_restaurants_by_radius

app = FastAPI()

class CityQuery(BaseModel):
    cities: List[str]
    radius: Optional[int] = 1000  # default radius in meters

@app.post("/restaurants")
def restaurants_endpoint(query: CityQuery):
    try:
        results = get_restaurants_by_radius(query.cities, query.radius)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === File: services/osm_service.py ===
import requests
import time

def get_city_coords(city_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city_name, "format": "json", "limit": 1}
    headers = {"User-Agent": "GrimoireOSM/1.0"}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    if not data:
        raise ValueError(f"No coordinates found for {city_name}")
    return float(data[0]["lat"]), float(data[0]["lon"])

def query_overpass_radius(lat, lon, radius):
    query = f"""
    [out:json][timeout:25];
    node["amenity"="restaurant"](around:{radius},{lat},{lon});
    out body;
    """
    url = "https://overpass-api.de/api/interpreter"
    response = requests.post(url, data={"data": query})
    response.raise_for_status()
    return response.json()

def extract_info(osm_data, city):
    restaurants = []
    for element in osm_data.get("elements", []):
        tags = element.get("tags", {})
        name = tags.get("name", "Unnamed")
        phone = tags.get("contact:phone") or tags.get("phone", "N/A")
        address = ", ".join(filter(None, [
            tags.get("addr:street", ""),
            tags.get("addr:housenumber", ""),
            tags.get("addr:postcode", ""),
            tags.get("addr:city", "")
        ]))
        lat = element.get("lat", "N/A")
        lon = element.get("lon", "N/A")
        restaurants.append({
            "City": city,
            "Name": name,
            "Address": address,
            "Phone": phone,
            "Latitude": lat,
            "Longitude": lon
        })
    return restaurants

def get_restaurants_by_radius(city_list, radius_m=1000):
    all_data = []
    for city in city_list:
        try:
            lat, lon = get_city_coords(city)
            data = query_overpass_radius(lat, lon, radius_m)
            results = extract_info(data, city)
            all_data.extend(results)
        except Exception as e:
            print(f"❌ Error for {city}: {e}")
        time.sleep(1.5)
    return all_data