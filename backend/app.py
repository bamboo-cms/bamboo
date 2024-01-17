import os

from dotenv import load_dotenv

from bamboo import create_app

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


config_name = os.getenv("FLASK_CONFIG", "development")
app = create_app(config_name)
