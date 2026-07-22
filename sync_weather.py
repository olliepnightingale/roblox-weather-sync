import os, time, json, requests

# Retrieve variables securely from GitHub Settings
ROBLOX_API_KEY = os.environ.get("ROBLOX_API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
ASSET_ID = os.environ.get("ASSET_ID")

CITIES = ["London", "New York", "Tokyo", "Paris", "Sydney"]

def get_live_weather():
    """Fetches real-time weather metrics using the requests params module."""
    weather_payload = {}
    base_url = "https://openweathermap.org"
    
    for city in CITIES:
        try:
            query_parameters = {
                "q": city,
                "appid": WEATHER_API_KEY,
                "units": "metric"
            }
            
            response = requests.get(base_url, params=query_parameters, timeout=10)
            
            # CORE SEPARATION: Check the status code directly before parsing JSON text
            if response.status_code == 200:
                data = response.json()
                weather_payload[city] = {
                    "temp": round(data["main"]["temp"], 1),
                    "condition": data["weather"]["main"]
                }
            else:
                # Reveals exactly what HTML/text error page the server responded with
                print(f"Server Rejection for {city}! HTTP Code: {response.status_code}")
                print(f"Raw Response snippet: {response.text[:200]}")
                
        except Exception as error:
            print(f"Execution fault for {city}: {error}")
            
    return weather_payload

def update_roblox_description(weather_data):
    """Pushes a simplified string payload directly into the Roblox metadata registry."""
    url = f"https://roblox.com{ASSET_ID}"
    headers = {"x-api-key": ROBLOX_API_KEY}
    
    json_string = json.dumps(weather_data, separators=(',', ':'))
    asset_metadata = {
        "assetId": str(ASSET_ID),
        "description": json_string
    }
    
    form_data = {
        "request": (None, json.dumps(asset_metadata), 'application/json')
    }
    
    response = requests.patch(url, headers=headers, files=form_data, timeout=15)
    print(f"Roblox Response Code: {response.status_code}")

if __name__ == "__main__":
    print("--- NEW WEATHER SYNC ENGINE ACTIVE ---")
    data = get_live_weather()
    print(f"Weather Data Collected: {json.dumps(data)}")
    if data and len(data) > 0:
        update_roblox_description(data)
