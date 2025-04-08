import os

class Config:
    # Base configuration
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Root directory of the project
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')  # Folder for uploaded files
    TEMP_FOLDER = os.path.join(BASE_DIR, 'temp')  # Temporary folder for processing
    PDF_REPORTS_FOLDER = os.path.join(BASE_DIR, 'PDFReports')  # Folder for PDF reports
    DB_PATH = os.path.join(BASE_DIR, 'db', 'report_data.db')  # Path to the SQLite DB file

    # Application Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max upload size 16MB (adjust as needed)
    ALLOWED_EXTENSIONS = {'pdf'}  # Only allow PDF uploads
