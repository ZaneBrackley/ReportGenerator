import sqlite3
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import Config

def create_tables(conn):
    try:
        cursor = conn.cursor()
        print("Creating tables...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY,
            name VARCHAR,
            description TEXT,
            last_user VARCHAR,
            domain VARCHAR,
            serial_number VARCHAR,
            os_version VARCHAR,
            architecture VARCHAR,
            windows_key VARCHAR,
            last_reboot TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hardware (
            id INTEGER PRIMARY KEY,
            device_id INTEGER NOT NULL,
            processor VARCHAR,
            ram INTEGER,
            motherboard VARCHAR,
            bios_version VARCHAR,
            display_adapter VARCHAR,
            build_date DATE,
            FOREIGN KEY (device_id) REFERENCES devices(id)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS storage (
            id INTEGER PRIMARY KEY,
            device_id INTEGER NOT NULL,
            drive_letter VARCHAR,
            disk_description VARCHAR,
            disk_size VARCHAR,
            disk_used VARCHAR,
            disk_usage_percent VARCHAR,
            FOREIGN KEY (device_id) REFERENCES devices(id)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS software (
            id INTEGER PRIMARY KEY,
            device_id INTEGER NOT NULL,
            office_key VARCHAR,
            antivirus VARCHAR,
            bitlocker_status VARCHAR,
            FOREIGN KEY (device_id) REFERENCES devices(id)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitoring (
            id INTEGER PRIMARY KEY,
            device_id INTEGER NOT NULL,
            network_ext_ip VARCHAR,
            network_int_ip VARCHAR,
            mac_address VARCHAR,
            FOREIGN KEY (device_id) REFERENCES devices(id)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY,
            device_id INTEGER NOT NULL,
            firewall_enabled BOOLEAN,
            defender_active BOOLEAN,
            last_scan TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES devices(id)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS backups (
            id INTEGER PRIMARY KEY,
            device_id INTEGER NOT NULL,
            backup_status VARCHAR,
            last_backup TIMESTAMP,
            restore_events INTEGER,
            FOREIGN KEY (device_id) REFERENCES devices(id)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_health (
            id INTEGER PRIMARY KEY,
            device_id INTEGER NOT NULL,
            status VARCHAR,
            issues TEXT,
            FOREIGN KEY (device_id) REFERENCES devices(id)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patch_management (
            id INTEGER PRIMARY KEY,
            device_id INTEGER NOT NULL,
            patch_name VARCHAR,
            patch_status VARCHAR,
            installed_at TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES devices(id)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS lifecycle (
            id INTEGER PRIMARY KEY,
            device_id INTEGER NOT NULL,
            purchase_date TIMESTAMP,
            warranty_date VARCHAR,
            warranty_status VARCHAR,
            FOREIGN KEY (device_id) REFERENCES devices(id)
        );
        """)

        conn.commit()

    except sqlite3.Error as e:
        print(f"SQLite error during table creation: {e}")
    finally:
        cursor.close()

def insert_device_info(conn, device_data):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO devices (name, description, last_user, domain, serial_number, os_version, architecture, windows_key, last_reboot)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (device_data['device']['device_name'],
          device_data['device']['description'],
          device_data['device']['last_user'],
          device_data['device']['domain'],
          device_data['device']['serial_number'],
          device_data['device']['os_version'],
          device_data['device']['architecture'],
          device_data['device'].get('windows_key', 'NA'),
          device_data['device']['last_reboot']))

    device_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO hardware (device_id, processor, ram, motherboard, bios_version, display_adapter)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (device_id,
          device_data['hardware']['cpu'],
          device_data['hardware']['ram'],
          device_data['hardware']['motherboard'],
          device_data['hardware']['bios_version'],
          device_data['hardware']['display_adapter']))

    for storage in device_data['storage']:
        cursor.execute("""
            INSERT INTO storage (device_id, drive_letter, disk_description, disk_size, disk_used, disk_usage_percent)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (device_id,
              storage['drive_letter'],
              storage['disk_description'],
              storage['disk_size'],
              storage['disk_used'],
              storage['disk_usage_percent']))

    cursor.execute("""
        INSERT INTO software (device_id, office_key, antivirus, bitlocker_status)
        VALUES (?, ?, ?, ?)
    """, (device_id,
          device_data['software']['office_key'],
          device_data['software']['antivirus'],
          device_data['software']['bitlocker_status']))

    cursor.execute("""
        INSERT INTO monitoring (device_id, network_ext_ip, network_int_ip, mac_address)
        VALUES (?, ?, ?, ?)
    """, (device_id,
          device_data['monitoring']['network_ext_ip'],
          device_data['monitoring']['network_int_ip'],
          device_data['monitoring']['mac_address']))
    
    cursor.execute("""
        INSERT INTO lifecycle (device_id, warranty_date, warranty_status)
        VALUES (?, ?, ?)
    """, (device_id,
          device_data['lifecycle']['warranty_date'],
          device_data['lifecycle']['warranty_status']))

    conn.commit()
