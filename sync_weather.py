import os, time, json, requests

# Retrieve variables securely from GitHub Settings
ROBLOX_API_KEY = os.environ.get("ROBLOX_API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
ASSET_ID = os.environ.get("ASSET_ID")

CITIES = ["London", "New York", "Tokyo", "Paris", "Sydney"]

def get_live_weather():
    """Fetches real-time weather metrics using a safe params dictionary configuration."""
    weather_payload = {}
    
    # Clean static URL path prevents system text-stripping bugs
    base_url = "https://openweathermap.org"
    
    for city in CITIES:
        try:
            # DYNAMIC ARGUMENTS: Requests handles formatting automatically
            query_parameters = {
                "q": city,
                "appid": WEATHER_API_KEY,
                "units": "metric"
            }
            
            # Execute standard GET call using parameter array maps
            response = requests.get(base_url, params=query_parameters, timeout=10)
            
            # IMPROVED LOGGING: Catch and display the real response code
            if response.status_code == 200:
                data = response.json()
                weather_payload[city] = {
                    "temp": round(data["main"]["temp"], 1),
                    "condition": data["weather"]["main"]
                }
            else:
                print(f"API Connection Rejected for {city}! HTTP Code: {response.status_code}")
                print(f"Server Response Content: {response.text[:150]}") # Only prints the first 150 letters to protect space

                
        except Exception as error:
            print("Execution fault for " + str(city) + ": " + str(error))
            
    return weather_payload

def update_roblox_description(weather_data):
    """Pushes a simplified string payload directly into the Roblox metadata registry."""
    url = "https://roblox.com" + str(ASSET_ID)
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
    print("Roblox Server Response Code: " + str(response.status_code))
    print("Roblox Server Text: " + str(response.text))

if __name__ == "__main__":
    print("--- NEW WEATHER SYNC ENGINE ACTIVE ---")
    data = get_live_weather()
    print("Weather Data Collected: " + json.dumps(data))
    if data and len(data) > 0:
        update_roblox_description(data)
