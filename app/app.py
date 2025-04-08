from flask import Flask, render_template, request
import sys, os
import pdfplumber
import camelot
import sqlite3

# Add parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import Config
from extractor_dispatcher import get_extractor
from database import create_tables, insert_device_info

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

    if request.method == 'POST':
        uploaded_files = request.files.getlist('file')

        # Drop all data whenever a new upload happens
        reset_database()

        for file in uploaded_files:
            if file.filename.endswith('.pdf'):
                file_path = os.path.join(app.config['TEMP_FOLDER'], file.filename)
                file.save(file_path)

                # Extract and store raw text
                all_text.append(extract_text_with_pdfplumber(file_path))

                # Read tables with Camelot
                tables = camelot.read_pdf(file_path, pages='2-end', flavor='lattice', line_scale=40)
                all_tables_html.extend([table.df.to_html(classes="table table-bordered") for table in tables])

                # Dispatch and parse using appropriate extractor
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

    return render_template('index.html', text="\n\n".join(all_text), tables=all_tables_html)


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
