import os
import yaml

class Config:
    """
    Configuration settings for the Flask app, including file paths and upload settings.
    """
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    DB_PATH = os.path.join(os.path.dirname(BASE_DIR), 'output', 'report_data.db')

    TEMP_FOLDER = os.path.join(os.path.dirname(BASE_DIR), 'temp')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf'}

    CONFIG_YAML = os.path.join(BASE_DIR, 'config.yml')

def load_sites():
    """
    Load site names from config.yaml.
    Returns a list of site names (keys in the 'sites' dictionary).
    """
    try:
        with open(Config.CONFIG_YAML, 'r') as file:
            config = yaml.safe_load(file)
            return list(config.get('sites', {}).keys())
    except Exception as e:
        print(f"Error loading config.yaml: {e}")
        return []