import os, time, json, requests

# Setup via GitHub Secrets
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
                    "humidity": data["main"]["humidity"],
                    "condition": data["weather"]["main"],
                    "updated": int(time.time())
                }
        except Exception as error: print(f"Error: {error}")
    return weather_payload

def generate_roblox_xml(weather_data):
    # Create valid .rbxm XML structure with escaped data
    json_string = json.dumps(weather_data, separators=(',', ':'))
    escaped_json = json_string.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<roblox version="4"><Item class="StringValue" Referent="RBX0">\n'
        f'<Properties><string name="Name">WeatherData</string>\n'
        f'<string name="Value">{escaped_json}</string></Properties>\n'
        '</Item></roblox>'
    )

def push_to_roblox_cloud(xml_content):
    url = f"https://roblox.com{ASSET_ID}?publish=true"
    headers = {"x-api-key": ROBLOX_API_KEY}
    # multipart/form-data payload required by Roblox
    form_data = {
        "request": (None, '{}', 'application/json'),
        "fileContent": ('model.rbxm', xml_content, 'application/octet-stream')
    }
    requests.patch(url, headers=headers, files=form_data, timeout=15)

if __name__ == "__main__":
    data = get_live_weather()
    if data: push_to_roblox_cloud(generate_roblox_xml(data))
