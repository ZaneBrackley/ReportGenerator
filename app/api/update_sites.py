import requests
import base64
import yaml
import os

from config.config import Config

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

def get_sites(api_url, token):
    url = f"{api_url}/api/v2/account/sites"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()

    if "sites" not in data:
        raise KeyError(f"'sites' key not found in response: {data}")

    return data["sites"]

def populate_sites():
    if not os.path.exists(Config.CONFIG_YAML):
        raise FileNotFoundError(f"Could not find config at {Config.CONFIG_YAML}")

    with open(Config.CONFIG_YAML, "r") as f:
        config = yaml.safe_load(f)

    api_info = config["api"]
    token = get_access_token(api_info["url"], api_info["key"], api_info["secret"])
    sites = get_sites(api_info["url"], token)

    # Sort sites alphabetically by 'name'
    sorted_sites = sorted(sites, key=lambda site: site["name"])

    # Update the config dictionary with sorted sites
    config["sites"] = {
        site["name"]: {"uid": site["uid"]}
        for site in sorted_sites
    }

    with open(Config.CONFIG_YAML, "w") as f:
        yaml.dump(config, f, sort_keys=False)