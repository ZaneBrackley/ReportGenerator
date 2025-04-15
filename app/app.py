from flask import Flask, render_template, request
import os
import pdfplumber
import camelot
import sqlite3

# Import configuration and other modules
from config.config import Config, load_sites
from api.datto_client import get_devices_for_site, get_device_audit
from api.update_sites import populate_sites
from core.extractor_dispatcher import get_extractor
from core.database import create_tables, insert_device_from_api

# Define template and static folder paths
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'static')
)

# Load configuration from config.py
app.config.from_object(Config)

# Ensure temp dir exists
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

def reset_database():
    os.makedirs(os.path.dirname(app.config['DB_PATH']), exist_ok=True)

    with sqlite3.connect(app.config['DB_PATH']) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        for table in [
            "devices", "hardware", "storage", "software", "monitoring",
            "security_events", "backups", "device_health",
            "patch_management", "lifecycle"
        ]:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")
        
        conn.commit()
        create_tables(conn)

# Clear DB at app start
reset_database()

@app.route('/', methods=['GET', 'POST'])
def index():
    all_text = []
    all_tables_html = []
    sites = load_sites()
    api_json_output = {}

    if request.method == 'POST':
        uploaded_files = request.files.getlist('file')
        selected_site = request.form.get('site')

        if not selected_site:
            return render_template('index.html', sites=sites, selected_site='', api_json=api_json_output)

        reset_database()

        # Step 1–3: Fetch and insert Datto site + device audit info
        api_json_output = get_devices_for_site(selected_site)
        if "devices" not in api_json_output:
            raise ValueError("No devices found in API response.")

        with sqlite3.connect(app.config['DB_PATH']) as conn:
            for device in api_json_output["devices"]:
                insert_device_from_api(conn, device)

    return render_template('index.html', sites=sites, selected_site=request.form.get('site', ''), api_json=api_json_output)

def extract_text_with_pdfplumber(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[1:]:  # Skip cover page
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
    return text.strip()

def initialize_sites():
    if not os.path.exists('config/config.yml') or not load_sites():
        populate_sites()


if __name__ == "__main__":
    initialize_sites()
    app.run(debug=True)
