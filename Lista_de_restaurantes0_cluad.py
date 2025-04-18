import requests
import time
import csv
from geopy.distance import geodesic

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

def find_nearby_cities(lat, lon, radius_km=70):
    """Find cities and towns around the given coordinates."""
    query = f"""
    [out:json][timeout:60];
    (
      node["place"~"city|town|village"](around:{radius_km * 1000},{lat},{lon});
      relation["place"~"city|town|village"](around:{radius_km * 1000},{lat},{lon});
    );
    out center;
    """
    url = "https://overpass-api.de/api/interpreter"
    response = requests.post(url, data={"data": query})
    response.raise_for_status()
    data = response.json()
    
    cities = []
    for element in data.get("elements", []):
        tags = element.get("tags", {})
        name = tags.get("name", "Unnamed")
        
        # For relations, the center point is provided
        city_lat = element.get("lat") or element.get("center", {}).get("lat")
        city_lon = element.get("lon") or element.get("center", {}).get("lon")
        
        if city_lat and city_lon:
            # Calculate distance from central city
            distance = geodesic((lat, lon), (city_lat, city_lon)).kilometers
            
            place_type = tags.get("place", "unknown")
            cities.append({
                "name": name,
                "type": place_type,
                "lat": city_lat,
                "lon": city_lon,
                "distance_km": round(distance, 2)
            })
    
    # Sort by distance
    cities.sort(key=lambda x: x["distance_km"])
    return cities

def query_restaurants_in_city(city_name, city_lat, city_lon, radius_m=5000):
    """Query Overpass API for restaurants in a specific city."""
    print(f"  🔍 Searching for restaurants in {city_name}")
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="restaurant"](around:{radius_m},{city_lat},{city_lon});
    );
    out body;
    """
    url = "https://overpass-api.de/api/interpreter"
    response = requests.post(url, data={"data": query})
    response.raise_for_status()
    return response.json()

def extract_restaurant_info(osm_data, city_name):
    """Extract restaurant information from Overpass data."""
    restaurants = []
    for element in osm_data.get("elements", []):
        tags = element.get("tags", {})
        name = tags.get("name", "Unnamed")
        cuisine = tags.get("cuisine", "Not specified")
        phone = tags.get("contact:phone") or tags.get("phone", "N/A")
        website = tags.get("website", "N/A")
        
        address = ", ".join(filter(None, [
            tags.get("addr:street", ""),
            tags.get("addr:housenumber", ""),
            tags.get("addr:postcode", ""),
            tags.get("addr:city", "")
        ]))
        
        lat = element.get("lat", "N/A")
        lon = element.get("lon", "N/A")
        
        restaurants.append({
            "City": city_name,
            "Name": name,
            "Cuisine": cuisine,
            "Address": address,
            "Phone": phone,
            "Website": website,
            "Latitude": lat,
            "Longitude": lon
        })
    return restaurants

def find_restaurants_in_region(central_city, city_radius_km=70, restaurant_radius_m=5000, max_cities=None):
    """Find restaurants in all cities around a central city."""
    print(f"📍 Starting search from central city: {central_city}")
    
    # Step 1: Get coordinates of central city
    center_lat, center_lon = get_city_coords(central_city)
    print(f"  Center coordinates: {center_lat}, {center_lon}")
    
    # Step 2: Find nearby cities
    nearby_cities = find_nearby_cities(center_lat, center_lon, radius_km=city_radius_km)
    print(f"  Found {len(nearby_cities)} nearby cities/towns")
    
    # Limit number of cities if specified
    if max_cities:
        nearby_cities = nearby_cities[:max_cities]
        print(f"  Limited to {max_cities} closest cities")
    
    all_restaurants = []
    
    # Always include the central city
    central_city_exists = False
    for city in nearby_cities:
        if city["name"].lower() == central_city.lower():
            central_city_exists = True
            break
    
    if not central_city_exists:
        nearby_cities.insert(0, {
            "name": central_city,
            "type": "city",
            "lat": center_lat,
            "lon": center_lon,
            "distance_km": 0
        })
    
    # Step 3: Find restaurants in each city
    for i, city in enumerate(nearby_cities):
        city_name = city["name"]
        city_lat = city["lat"]
        city_lon = city["lon"]
        city_type = city["type"]
        distance = city["distance_km"]
        
        print(f"\n🏙️  [{i+1}/{len(nearby_cities)}] Searching in {city_name} ({city_type}, {distance}km away)")
        
        try:
            # Get restaurants
            restaurant_data = query_restaurants_in_city(city_name, city_lat, city_lon, restaurant_radius_m)
            restaurants = extract_restaurant_info(restaurant_data, city_name)
            
            print(f"  ✅ Found {len(restaurants)} restaurants in {city_name}")
            all_restaurants.extend(restaurants)
        except Exception as e:
            print(f"  ❌ Error searching {city_name}: {e}")
        
        # Be nice to the API
        time.sleep(1.5)
    
    return all_restaurants

def save_to_csv(restaurants, output_file="regional_restaurants.csv"):
    """Save restaurant data to CSV file."""
    if not restaurants:
        print("No restaurants to save!")
        return
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["City", "Name", "Cuisine", "Address", "Phone", "Website", "Latitude", "Longitude"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(restaurants)
    
    print(f"\n💾 Saved {len(restaurants)} restaurants to {output_file}")

def main():
    central_city = input("Enter the central city name: ")
    city_radius = float(input("Enter radius to search for cities (km) [default=70]: ") or "70")
    restaurant_radius = float(input("Enter radius to search for restaurants around each city (m) [default=5000]: ") or "5000")
    max_cities_input = input("Maximum number of cities to search (leave empty for all): ")
    max_cities = int(max_cities_input) if max_cities_input else None
    
    output_file = input("Output CSV filename [default=regional_restaurants.csv]: ") or "regional_restaurants.csv"
    
    restaurants = find_restaurants_in_region(
        central_city, 
        city_radius_km=city_radius, 
        restaurant_radius_m=restaurant_radius,
        max_cities=max_cities
    )
    
    save_to_csv(restaurants, output_file)
    
    print(f"\n🎉 Found a total of {len(restaurants)} restaurants in the region around {central_city}!")

if __name__ == "__main__":
    main()