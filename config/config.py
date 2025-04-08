import os

class Config:
    # Base configuration
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # This will point to 'root/config'
    
    # Update DB_PATH to point to the correct path in the root directory
    DB_PATH = os.path.join(os.path.dirname(BASE_DIR), 'db', 'report_data.db')  # Points to 'root/db/report_data.db'

    # Additional configuration...
    TEMP_FOLDER = os.path.join(os.path.dirname(BASE_DIR), 'temp')  # Temporary folder for processing
    PDF_REPORTS_FOLDER = os.path.join(os.path.dirname(BASE_DIR), 'PDFReports')  # Folder for PDF reports
    
    # Application Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max upload size 16MB (adjust as needed)
    ALLOWED_EXTENSIONS = {'pdf'}  # Only allow PDF uploads
