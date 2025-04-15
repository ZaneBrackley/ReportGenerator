from flask import Flask, render_template, request
import os
import pdfplumber
import camelot
import sqlite3

# Import configuration and other modules
from config.config import Config, load_sites
from api.datto_client import get_devices_for_site
from core.extractor_dispatcher import get_extractor
from core.database import create_tables, insert_device_info

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
        selected_site = request.form.get('site')  # Get selected site from form

        if selected_site:
            try:
                api_json_output = get_devices_for_site(selected_site)
            except Exception as e:
                api_json_output = {"error": f"Failed to fetch API data: {e}"}

        reset_database()

        for file in uploaded_files:
            if file.filename.endswith('.pdf'):
                file_path = os.path.join(app.config['TEMP_FOLDER'], file.filename)
                file.save(file_path)

                all_text.append(extract_text_with_pdfplumber(file_path))

                tables = camelot.read_pdf(file_path, pages='2-end', flavor='lattice', line_scale=40)
                all_tables_html.extend([table.df.to_html(classes="table table-bordered") for table in tables])

                try:
                    extractor = get_extractor(file.filename)(file_path, tables)
                    parsed_devices = extractor.parse()

                    with sqlite3.connect(app.config['DB_PATH']) as conn:
                        for device_info in parsed_devices:
                            insert_device_info(conn, device_info)

                except ValueError as e:
                    all_text.append(f"Unsupported file: {file.filename} - {str(e)}")

                os.remove(file_path)
            else:
                all_text.append(f"Invalid file type: {file.filename}. Please upload PDF files only.")

    return render_template('index.html', text="\n\n".join(all_text),
                           tables=all_tables_html,
                           sites=sites,
                           selected_site=request.form.get('site', ''),
                           api_json=api_json_output)


def extract_text_with_pdfplumber(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[1:]:  # Skip cover page
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
    return text.strip()


if __name__ == "__main__":
    app.run(debug=True)
