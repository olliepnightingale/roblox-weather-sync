import os
import time
import json
import requests

# 1. Pull secure configuration variables from Render's environment
ROBLOX_API_KEY = os.environ.get("ROBLOX_API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
ASSET_ID = os.environ.get("ASSET_ID")

# The tracking cities (Feel free to modify or add more locations here)
CITIES = ["London", "New York", "Tokyo", "Paris", "Sydney"]

def get_live_weather():
    """Fetches real-time temperature and weather metrics for target cities."""
    weather_payload = {}
    
    for city in CITIES:
        try:
            # Request metric temperature data from the OpenWeather API
            url = f"https://openweathermap.org{city}&appid={WEATHER_API_KEY}&units=metric"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                weather_payload[city] = {
                    "temp": round(data["main"]["temp"], 1),
                    "humidity": data["main"]["humidity"],
                    "condition": data["weather"][0]["main"],
                    "updated": int(time.time())
                }
            else:
                print(f"Weather API error for {city}: {response.status_code}")
        except Exception as error:
            print(f"Failed pulling weather for {city}: {error}")
            
    return weather_payload

def generate_roblox_xml(weather_data):
    """Wraps weather JSON inside an official Roblox .rbxm structural format."""
    # Convert data dictionary to a clean, human-readable JSON string
    json_string = json.dumps(weather_data, indent=2)
    
    # Escape crucial XML special characters so the Roblox file formatting doesn't break
    escaped_json = json_string.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    # Standard Roblox Model File Template (.rbxm) housing our StringValue container
    rbxm_contents = f"""<roblox xmlns:xmime="http://w3.org" xmlns:xsi="http://w3.org" xsi:noNamespaceSchemaLocation="http://roblox.com" version="4">
	<Item class="StringValue" Referent="RBX0">
		<Properties>
			<string name="Name">WeatherData</string>
			<string name="Value">{escaped_json}</string>
		</Properties>
	</Item>
</roblox>"""
    return rbxm_contents

def push_to_roblox_cloud(xml_content):
    """Pushes the new rbxm model structure directly to the Roblox Asset ID."""
    url = f"https://apis.roblox.com/assets/v1/assets/{ASSET_ID}"
    
    headers = {
        "x-api-key": ROBLOX_API_KEY
    }
    
    # Assets API updates require a multipart metadata config form + the physical file body
    form_data = {
        "request": (None, '{}', 'application/json'),
        "fileContent": ('model.rbxm', xml_content, 'application/octet-stream')
    }
    
    try:
        # Patch updates the existing target asset instead of generating new ids
        response = requests.patch(url, headers=headers, files=form_data, timeout=15)
        if response.status_code in [200, 202]:
            print(f"Successfully uploaded updated data to Roblox Asset ID: {ASSET_ID}")
        else:
            print(f"Roblox API rejection. Code: {response.status_code} | Text: {response.text}")
    except Exception as error:
        print(f"Failed contacting Roblox servers: {error}")

def start_sync_loop():
    """Main worker thread managing continuous synchronization intervals."""
    print("Weather Sync Engine Started.")
    while True:
        # Fetch data
        current_weather = get_live_weather()
        
        if current_weather:
            # Construct file template
            roblox_file = generate_roblox_xml(current_weather)
            # Send file to cloud container
            push_to_roblox_cloud(roblox_file)
        
        # Idle for 15 minutes before collecting data again to avoid API rate limits
        print("Sleeping for 15 minutes...")
        time.sleep(900)

if __name__ == "__main__":
    start_sync_loop()
