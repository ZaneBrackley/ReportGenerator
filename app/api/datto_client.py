import requests
import base64
import yaml

from config.config import Config

def load_config():
    with open(Config.CONFIG_YAML, 'r') as f:
        return yaml.safe_load(f)
    
config = load_config()

api_url = config["api"]["url"]
api_key = config["api"]["key"]
api_secret = config["api"]["secret"]

def get_access_token(api_url, api_key, api_secret):
    url = f"{api_url}/auth/oauth/token"
    data = {
        "username": api_key,
        "password": api_secret,
        "grant_type": "password"
    }
    headers = {
        "Authorization": f"Basic {base64.b64encode(b'public-client:public').decode('utf-8')}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

token = get_access_token(api_url, api_key, api_secret)
headers = {"Authorization": f"Bearer {token}"}

def get_devices_for_site(site_name):
    config = load_config()

    if site_name not in config["sites"]:
        raise ValueError(f"Site '{site_name}' not found in config.yaml")

    site_uid = config["sites"][site_name]["uid"]
    url = f"{api_url}/api/v2/site/{site_uid}/devices"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_device_audit(device_uid):
    """
    Fetch audit details for a specific device based on its UID.
    """
    url = f"{api_url}/api/v2/audit/device/{device_uid}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()