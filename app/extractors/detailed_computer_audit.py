from .base_extractor import BaseExtractor
import pandas as pd

class DetailedComputerAuditExtractor(BaseExtractor):
    def __init__(self, filepath, tables):
        super().__init__(filepath)
        self.tables = tables  # <--- store tables as instance attribute

    def parse(self):
        devices = []
        def get_value(row, key):
            for item in row:
                if item.strip().startswith(key):
                    return item.split(":", 1)[-1].strip()
            return ""

        def group_tables(tables, chunk_size=7):
            table_dfs = [table.df for table in tables]
            grouped_dfs = []
            for i in range(0, len(table_dfs), chunk_size):
                grouped_dfs.append(pd.concat(table_dfs[i:i + chunk_size], ignore_index=True))
            return grouped_dfs

        grouped_tables = group_tables(self.tables)  # <--- use self.tables here

        for group in grouped_tables:
            # Device dictionary with a 'device' key
            device = {
                "device": {  # The 'device' key should exist
                    "device_name": "",
                    "description": "",
                    "domain": "",
                    "last_user": "",
                    "serial_number": "",
                    "os_version": "",
                    "architecture": "",
                    "last_reboot": "",
                },
                "hardware": {
                    "cpu": "",
                    "ram": "",
                    "motherboard": "",
                    "bios_version": "",
                    "display_adapter": ""
                },
                "software": {
                    "office_key": "",
                    "antivirus": "",
                    "bitlocker_status": ""
                },
                "monitoring": {
                    "network_ext_ip": "",
                    "network_int_ip": "",
                    "mac_address": ""
                },
                "security_events": {
                    "firewall_enabled": "",
                    "defender_active": "",
                    "last_scan": ""
                },
                "backups": {
                    "backup_status": "",
                    "last_backup": ""
                },
                "device_health": {
                    "status": "",
                    "issues": ""
                },
                "patch_management": {
                    "pending_updates": "",
                    "last_patch_date": ""
                },
                "lifecycle": {
                    "purchase_date": "",
                    "warranty_expiry": ""
                },
                "storage": []  # To store multiple storage devices
            }

            rows = group.astype(str).map(str.strip).values.tolist()

            rows_with_next = zip(rows, rows[1:] + [[""] * len(rows[0])])  # Handles end-of-list safely

            for row, next_row in rows_with_next:
                if "Device Name:" in row[0]:
                    device["device"]["device_name"] = get_value(row, "Device Name")
                elif "Description:" in row[0]:
                    device["device"]["description"] = get_value(row, "Description")
                elif "Domain:" in row[0]:
                    device["device"]["domain"] = get_value(row, "Domain")
                elif "Last User:" in row[0]:
                    device["device"]["last_user"] = get_value(row, "Last User")
                elif "Serial Number:" in row[0]:
                    device["device"]["serial_number"] = get_value(row, "Serial Number")
                elif "Last Reboot:" in row[0]:
                    device["device"]["last_reboot"] = get_value(row, "Last Reboot")
                elif "Operating System:" in row[0]:
                    device["device"]["os_version"] = get_value(row, "Operating System")
                elif "OS Architecture:" in row[0]:
                    device["device"]["architecture"] = get_value(row, "OS Architecture")
                elif "Windows Activation Key:" in row[0]:
                    device["device"]["windows_key"] = get_value(row, "Windows Activation Key")

                elif "Processor:" in row[0]:
                    device["hardware"]["cpu"] = get_value(row, "Processor")
                elif "Memory:" in row[0]:
                    device["hardware"]["ram"] = get_value(row, "Memory")
                elif "Motherboard:" in row[0]:
                    device["hardware"]["motherboard"] = get_value(row, "Motherboard")
                elif "BIOS Name:" in row[0]:
                    device["hardware"]["bios_version"] = get_value(row, "BIOS Name")
                elif "Display Adapter" in row[0]:
                    device["hardware"]["display_adapter"] = next_row[0].strip()
                elif "Office Activation Key:" in row[0]:
                    device["software"]["office_key"] = get_value(row, "Office Activation Key")
                elif "BitLocker Detail:" in row[0]:
                    device["software"]["bitlocker_status"] = get_value(row, "BitLocker Detail")
                elif "Antivirus Product:" in row[0]:
                    device["software"]["antivirus"] = get_value(row, "Antivirus Product")

                elif "Ext IP Address:" in row[0]:
                    device["monitoring"]["network_ext_ip"] = get_value(row, "Ext IP Address")
                elif "Int IP Address:" in row[0]:
                    device["monitoring"]["network_int_ip"] = get_value(row, "Int IP Address")
                elif "Realtek" in row[0] or "MAC Address" in row[0]:
                    device["monitoring"]["mac_address"] = row[-1].strip()

                elif "Local Fixed Disk" in row:
                    # Add each storage device as a separate entry
                    storage_device = {
                        "drive_letter": row[0] if len(row) > 1 else "",
                        "disk_description": row[1] if len(row) > 1 else "",
                        "disk_size": row[2] if len(row) > 2 else "",
                        "disk_used": row[3] if len(row) > 3 else "",
                        "disk_usage_percent": row[4] if len(row) > 4 else ""
                    }
                    device["storage"].append(storage_device)

            # Now add the device and its storage devices to the devices list
            devices.append(device)

        return devices
