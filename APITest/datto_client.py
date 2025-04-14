import requests
import yaml
import os
import json
import base64

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.yaml")

    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def get_access_token(api_url, api_key, api_secret):
    url = f"{api_url}/auth/oauth/token"
    data = {
        "username": api_key,
        "password": api_secret,
        "grant_type": "password"
    }

    auth_string = base64.b64encode(b"public-client:public").decode("utf-8")
    headers = {
        "Authorization": f"Basic {auth_string}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

def get_devices(api_url, token, site_uid):
    url = f"{api_url}/api/v2/site/{site_uid}/devices"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def save_to_file(data):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "devices_output.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2))
    print(f"✅ Device data saved to {output_path}")

if __name__ == "__main__":
    config = load_config()

    api_url = config["api"]["url"]
    api_key = config["api"]["KEY"]
    api_secret = config["api"]["SECRET"]
    site_uid = config["sites"]["site_name"]["uid"]

    token = get_access_token(api_url, api_key, api_secret)

    devices = get_devices(api_url, token, site_uid)

    save_to_file(devices)
