import requests
import yaml
import os
import base64
import json
import sys

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

def save_devices_to_json(data, site_name):
    output_path = f"{site_name}_devices.json"
    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"✅ Saved {len(data.get('devices', []))} devices to: {output_path}")
    return data.get("devices", [])

def get_device_audit(api_url, token, device_uid):
    url = f"{api_url}/api/v2/audit/device/{device_uid}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def save_device_audit_to_json(device_uid, audit_data):
    output_path = f"{device_uid}_audit.json"
    with open(output_path, "w") as f:
        json.dump(audit_data, f, indent=4)
    print(f"✅ Saved audit data for device UID '{device_uid}' to: {output_path}")

def choose_site(sites):
    site_names = list(sites.keys())
    print("Available sites:")
    for index, name in enumerate(site_names, start=1):
        print(f"{index}. {name}")

    site_choice = input("Choose a site by name or number: ")

    if site_choice.isdigit():
        site_index = int(site_choice) - 1
        if 0 <= site_index < len(site_names):
            return site_names[site_index]
        else:
            print("Invalid site number.")
            sys.exit(1)
    else:
        for name in site_names:
            if name.lower() == site_choice.lower():
                return name
        print(f"Site '{site_choice}' not found.")
        sys.exit(1)

if __name__ == "__main__":
    config = load_config()

    site_name = choose_site(config["sites"])

    if site_name not in config["sites"]:
        print(f"❌ Site '{site_name}' not found in config.")
        sys.exit(1)

    site_uid = config["sites"][site_name]["uid"]
    api_url = config["api"]["url"]
    api_key = config["api"]["KEY"]
    api_secret = config["api"]["SECRET"]

    token = get_access_token(api_url, api_key, api_secret)
    devices = get_devices(api_url, token, site_uid)

    # Save site devices to a JSON file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    devices_json_path = os.path.join(script_dir, f"site_devices_{site_uid}.json")
    with open(devices_json_path, "w") as f:
        json.dump(devices, f, indent=2)
    print(f"✅ Saved site devices JSON to: {devices_json_path}")

    # Ask user for device UID
    device_uid = input("Enter a device UID to fetch its audit data: ").strip()
    if not device_uid:
        print("❌ No device UID provided.")
        sys.exit(1)

    audit_data = get_device_audit(api_url, token, device_uid)

    # Save audit data to a JSON file
    audit_json_path = os.path.join(script_dir, f"device_audit_{device_uid}.json")
    with open(audit_json_path, "w") as f:
        json.dump(audit_data, f, indent=2)
    print(f"✅ Saved device audit JSON to: {audit_json_path}")