import os, time, json, requests

ROBLOX_API_KEY = os.environ.get("ROBLOX_API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
ASSET_ID = os.environ.get("ASSET_ID")
CITIES = ["London", "New York", "Tokyo", "Paris", "Sydney"]

def get_live_weather():
    weather_payload = {}
    for city in CITIES:
        try:
            url = f"https://openweathermap.org{city}&appid={WEATHER_API_KEY}&units=metric"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                weather_payload[city] = {
                    "temp": round(data["main"]["temp"], 1),
                    "condition": data["weather"]["main"]
                }
        except Exception: pass
    return weather_payload

def update_roblox_description(weather_data):
    url = f"https://roblox.com{ASSET_ID}"
    headers = {"x-api-key": ROBLOX_API_KEY}
    
    # Compress JSON into a single line to fit in the description
    json_string = json.dumps(weather_data, separators=(',', ':'))
    
    # We update the metadata config block directly instead of uploading a file content stream
    form_data = {
        "request": (None, json.dumps({
            "assetId": ASSET_ID,
            "description": json_string # Your live weather data lives here now!
        }), 'application/json')
    }
    
    requests.patch(url, headers=headers, files=form_data, timeout=15)

if __name__ == "__main__":
    data = get_live_weather()
    if data: update_roblox_description(data)
