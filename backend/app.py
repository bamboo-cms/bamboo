import os
from pathlib import Path

from dotenv import load_dotenv

from bamboo import create_app

dotenv_path = Path(__file__).parent.resolve().joinpath(".env")
if dotenv_path.exists():
    load_dotenv(dotenv_path)


config_name = os.getenv("FLASK_CONFIG", "development")
app = create_app(config_name)
