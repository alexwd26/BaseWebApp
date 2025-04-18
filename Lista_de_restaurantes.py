import requests
import time
import csv

def get_city_coords(city_name):
    """Use Nominatim to get city center lat/lon."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city_name, "format": "json", "limit": 1}
    response = requests.get(url, params=params, headers={"User-Agent": "GrimoireOSM/1.0"})
    response.raise_for_status()
    data = response.json()
    if not data:
        raise ValueError(f"No coordinates found for {city_name}")
    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])
    return lat, lon

def query_overpass_radius(lat, lon, radius):
    """Query Overpass API for restaurants around city center."""
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="restaurant"](around:{radius},{lat},{lon});
    );
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

def get_restaurants_by_radius(city_list, radius_m=1000, output_csv="restaurants_radius.csv"):
    all_data = []
    for city in city_list:
        print(f"📍 Searching around {city} (radius: {radius_m}m)")
        try:
            lat, lon = get_city_coords(city)
            data = query_overpass_radius(lat, lon, radius_m)
            results = extract_info(data, city)
            all_data.extend(results)
        except Exception as e:
            print(f"❌ Failed for {city}: {e}")
        time.sleep(1.5)
    
    with open(output_csv, mode="w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["City", "Name", "Address", "Phone", "Latitude", "Longitude"])
        writer.writeheader()
        writer.writerows(all_data)
    
    print(f"\n✅ Saved {len(all_data)} restaurants to {output_csv}")
    return all_data

# Example:
cities = ["Cruz Alta"]
get_restaurants_by_radius(cities, radius_m=70000)
