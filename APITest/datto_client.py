import requests
import yaml
import os
import base64
import sqlite3
import sys
import json

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

def site_devices_db(data):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "devices.db")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT,
            site_uid TEXT,
            site_name TEXT,
            hostname TEXT,
            int_ip TEXT,
            ext_ip TEXT,
            os TEXT,
            last_user TEXT,
            domain TEXT,
            av_product TEXT,
            av_status TEXT,
            last_seen TEXT,
            last_reboot TEXT,
            creation_date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_udfs (
            device_uid TEXT,
            udf_key TEXT,
            udf_value TEXT,
            FOREIGN KEY(device_uid) REFERENCES devices(uid)
        )
    ''')

    for device in data.get("devices", []):
        cursor.execute('''
            INSERT INTO devices (
                uid, site_uid, site_name, hostname, int_ip, ext_ip, os,
                last_user, domain, av_product, av_status, last_seen,
                last_reboot, creation_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            device.get("uid"),
            device.get("siteUid"),
            device.get("siteName"),
            device.get("hostname"),
            device.get("intIpAddress"),
            device.get("extIpAddress"),
            device.get("operatingSystem"),
            device.get("lastLoggedInUser"),
            device.get("domain"),
            device.get("antivirus", {}).get("antivirusProduct"),
            device.get("antivirus", {}).get("antivirusStatus"),
            device.get("lastSeen"),
            device.get("lastReboot"),
            device.get("creationDate")
        ))

        udf = device.get("udf", {})
        for key, value in udf.items():
            if value and value.strip().lower() != "string":
                cursor.execute('''
                    INSERT INTO device_udfs (device_uid, udf_key, udf_value)
                    VALUES (?, ?, ?)
                ''', (device.get("uid"), key, value))

    conn.commit()
    conn.close()
    print(f"✅ Saved {len(data.get('devices', []))} devices to: {db_path}")

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

def get_all_device_uids():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "devices.db")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT uid FROM devices")
    uids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return uids

def get_device_audit(api_url, token, device_uid):
    url = f"{api_url}/api/v2/audit/device/{device_uid}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def device_audit_db(device_uid, audit_data):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "devices.db")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_uid TEXT,
            portal_url TEXT,
            web_remote_url TEXT,
            manufacturer TEXT,
            model TEXT,
            total_physical_memory INTEGER,
            username TEXT,
            dotnet_version TEXT,
            total_cpu_cores INTEGER,
            bios_serial TEXT,
            bios_release_date TEXT,
            bios_version TEXT,
            baseboard_manufacturer TEXT,
            baseboard_product TEXT,
            snmp_name TEXT,
            snmp_contact TEXT,
            snmp_location TEXT,
            snmp_uptime TEXT,
            snmp_serial TEXT,
            object_id TEXT,
            nic_summary TEXT,              -- JSON or summary string
            display_summary TEXT,          -- JSON or summary string
            disks_summary TEXT,            -- JSON or summary string
            processors TEXT,               -- CSV or single string
            video_boards TEXT,             -- CSV or single string
            attached_devices TEXT,         -- JSON or summary
            physical_memory TEXT           -- JSON or summary
        )
    ''')
    
    system = audit_data.get("systemInfo", {})
    bios = audit_data.get("bios", {})
    base = audit_data.get("baseBoard", {})
    snmp = audit_data.get("snmpInfo") or {}

    cursor.execute('''
        INSERT INTO device_audits (
            device_uid, portal_url, web_remote_url,
            manufacturer, model, total_physical_memory, username, dotnet_version, total_cpu_cores,
            bios_serial, bios_release_date, bios_version,
            baseboard_manufacturer, baseboard_product,
            snmp_name, snmp_contact, snmp_location, snmp_uptime, snmp_serial, object_id,
            nic_summary, display_summary, disks_summary,
            processors, video_boards, attached_devices, physical_memory
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        device_uid,
        audit_data.get("portalUrl"),
        audit_data.get("webRemoteUrl"),
        system.get("manufacturer"),
        system.get("model"),
        system.get("totalPhysicalMemory"),
        system.get("username"),
        system.get("dotNetVersion"),
        system.get("totalCpuCores"),
        bios.get("serialNumber"),
        bios.get("releaseDate"),
        bios.get("smBiosVersion"),
        base.get("manufacturer"),
        base.get("product"),
        snmp.get("snmpName"),
        snmp.get("snmpContact"),
        snmp.get("snmpLocation"),
        snmp.get("snmpUptime"),
        snmp.get("snmpSerial"),
        snmp.get("objectId"),
        json.dumps(audit_data.get("nics", [])),
        json.dumps(audit_data.get("displays", [])),
        json.dumps(audit_data.get("logicalDisks", [])),
        ", ".join(p["name"] for p in audit_data.get("processors", [])),
        ", ".join(v["displayAdapter"] for v in audit_data.get("videoBoards", [])),
        json.dumps(audit_data.get("attachedDevices", [])),
        json.dumps(audit_data.get("physicalMemory", []))
    ))

    conn.commit()
    conn.close()
    print(f"✅ Saved audit data for device: {device_uid} to: {db_path}")


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
    site_devices_db(devices)
    uids = get_all_device_uids()
    for uid in uids:
        audit_data = get_device_audit(api_url, token, uid)
        device_audit_db(uid, audit_data)