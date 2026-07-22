import os
import time
import json
import requests

# Pull secure configuration variables from GitHub Secrets
ROBLOX_API_KEY = os.environ.get("ROBLOX_API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
ASSET_ID = os.environ.get("ASSET_ID")

CITIES = ["London", "New York", "Tokyo", "Paris", "Sydney"]

def generate_roblox_xml(weather_data):
    """Wraps compressed weather JSON inside an official Roblox .rbxm structure."""
    # CRITICAL FIX: Remove indent and separators to compress the entire JSON into a single line
    json_string = json.dumps(weather_data, separators=(',', ':'))
    
    # Escape crucial XML characters so the structural tagging doesn't break
    escaped_json = json_string.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    return f"""<roblox xmlns:xmime="http://w3.org" xmlns:xsi="http://w3.org" xsi:noNamespaceSchemaLocation="http://roblox.com" version="4">
	<Item class="StringValue" Referent="RBX0">
		<Properties>
			<string name="Name">WeatherData</string>
			<string name="Value">{escaped_json}</string>
		</Properties>
	</Item>
</roblox>"""


def generate_roblox_xml(weather_data):
    json_string = json.dumps(weather_data, indent=2)
    escaped_json = json_string.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    return f"""<roblox xmlns:xmime="http://w3.org" xmlns:xsi="http://w3.org" xsi:noNamespaceSchemaLocation="http://roblox.com" version="4">
	<Item class="StringValue" Referent="RBX0">
		<Properties>
			<string name="Name">WeatherData</string>
			<string name="Value">{escaped_json}</string>
		</Properties>
	</Item>
</roblox>"""

def push_to_roblox_cloud(xml_content):
    url = f"https://roblox.com{ASSET_ID}"
    headers = {"x-api-key": ROBLOX_API_KEY}
    form_data = {
        "request": (None, '{}', 'application/json'),
        "fileContent": ('model.rbxm', xml_content, 'application/octet-stream')
    }
    
    try:
        response = requests.patch(url, headers=headers, files=form_data, timeout=15)
        if response.status_code in [200, 202]:
            print("Successfully uploaded updated data to Roblox!")
        else:
            print(f"Roblox API rejection: {response.status_code} - {response.text}")
    except Exception as error:
        print(f"Failed contacting Roblox servers: {error}")

if __name__ == "__main__":
    # Run once per trigger execution
    current_weather = get_live_weather()
    if current_weather:
        roblox_file = generate_roblox_xml(current_weather)
        push_to_roblox_cloud(roblox_file)
