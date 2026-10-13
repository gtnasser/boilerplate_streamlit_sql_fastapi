# core/config.py

import os
from dotenv import load_dotenv

load_dotenv()

# Define se o sistema roda em modo "local" ou "api"
APP_MODE = os.getenv("APP_MODE", "local")  # Opções: "local" ou "api"
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
