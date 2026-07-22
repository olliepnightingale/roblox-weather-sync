import os, time, json, requests

# Retrieve variables securely from GitHub Settings
ROBLOX_API_KEY = os.environ.get("ROBLOX_API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
ASSET_ID = os.environ.get("ASSET_ID")

CITIES = ["London", "New York", "Tokyo", "Paris", "Sydney"]

def get_live_weather():
    """Fetches weather metrics using the raw working browser URL format."""
    weather_payload = {}
    for city in CITIES:
        try:
            # FIXED: Built using explicit string concatenation to match your successful browser test
            url = "https://api.openweathermap.org/data/2.5/weather?q=" + str(city) + "&appid=" + str(WEATHER_API_KEY)
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                weather_payload[city] = {
                    "temp": round(data["main"]["temp"], 1),
                    "condition": data["weather"]["main"]
                }
            else:
                print("API Rejection for " + str(city) + "! Code: " + str(response.status_code))
                
        except Exception as error:
            print("Execution fault for " + str(city) + ": " + str(error))
    return weather_payload

def update_roblox_description(weather_data):
    """Pushes the minified weather string payload into the Roblox description metadata."""
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
