import sqlite3
import datetime

def create_tables(conn):
    try:
        cursor = conn.cursor()

        # Devices table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY,
            uid TEXT UNIQUE,
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

        # Hardware table
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

        # Storage table
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

        # Software table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS software (
            id INTEGER PRIMARY KEY,
            device_id INTEGER NOT NULL,
            office_key VARCHAR,
            antivirus VARCHAR,
            bitlocker_status VARCHAR,
            software_status VARCHAR,
            FOREIGN KEY (device_id) REFERENCES devices(id)
        );
        """)

        # Monitoring table
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

        # Security Events table
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

        # Backups table
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

        # Device Health table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_health (
            id INTEGER PRIMARY KEY,
            device_id INTEGER NOT NULL,
            status VARCHAR,
            issues TEXT,
            FOREIGN KEY (device_id) REFERENCES devices(id)
        );
        """)

        # Patch Management table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patch_management (
            id INTEGER PRIMARY KEY,
            device_id INTEGER NOT NULL,
            patch_status VARCHAR,
            patches_approved_pending VARCHAR,
            patches_not_approved VARCHAR,
            patches_installed VARCHAR,
            FOREIGN KEY (device_id) REFERENCES devices(id)
        );
        """)

        # Lifecycle table
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

        # UDFs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS udfs (
            id INTEGER PRIMARY KEY,
            device_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            FOREIGN KEY (device_id) REFERENCES devices(id)
        );
        """)

        conn.commit()

    except sqlite3.Error as e:
        print(f"SQLite error during table creation: {e}")
    finally:
        cursor.close()

def insert_device_from_api(conn, api_data):
    cursor = conn.cursor()

    # Insert into devices
    cursor.execute("""
        INSERT OR IGNORE INTO devices (uid, name, description, last_user, domain, os_version, serial_number)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        api_data.get("uid"),
        api_data.get("hostname"),
        api_data.get("description"),
        api_data.get("lastLoggedInUser"),
        api_data.get("domain"),
        api_data.get("operatingSystem"),
        api_data.get("serialNumber"),  # If serial number is available in the API, include it.
    ))

    # Get device ID
    cursor.execute("SELECT id FROM devices WHERE uid = ?", (api_data.get("uid"),))
    row = cursor.fetchone()
    if not row:
        print(f"Failed to fetch device ID for UID: {api_data.get('uid')}")
        return
    device_id = row[0]

    # Insert into software (including antivirus and software status)
    cursor.execute("""
        INSERT INTO software (device_id, antivirus, software_status)
        VALUES (?, ?, ?)
    """, (
        device_id,
        api_data.get("antivirus", {}).get("antivirusProduct"),
        api_data.get("softwareStatus"),
    ))

    # Insert patch management info
    cursor.execute("""
        INSERT INTO patch_management (device_id, patch_status, patches_approved_pending, patches_not_approved, patches_installed)
        VALUES (?, ?, ?, ?, ?)
    """, (
        device_id,
        api_data.get("patchManagement").get("patchStatus"),
        api_data.get("patchManagement").get("patchesApprovedPending"),
        api_data.get("patchManagement").get("patchesNotApproved"),
        api_data.get("patchManagement").get("patchesInstalled")
    ))

    # Insert into monitoring
    cursor.execute("""
        INSERT INTO monitoring (device_id, network_ext_ip, network_int_ip)
        VALUES (?, ?, ?)
    """, (
        device_id,
        api_data.get("extIpAddress"),
        api_data.get("intIpAddress"),
    ))

    # Insert into lifecycle (warranty info)
    cursor.execute("""
        INSERT INTO lifecycle (device_id, warranty_date)
        VALUES (?, ?)
    """, (
        device_id,
        api_data.get("warrantyDate")
    ))

    # Insert UDFs
    for key, value in api_data.get("udf", {}).items():
        if value and str(value).lower() != "null":
            cursor.execute("""
                INSERT INTO udfs (device_id, key, value)
                VALUES (?, ?, ?)
            """, (device_id, key, str(value)))

    conn.commit()
    cursor.close()