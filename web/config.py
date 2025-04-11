# web/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações da aplicação web
APP_NAME = "Medical Diagnosis System"
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")
API_KEY = os.getenv("API_KEY", "bb591da6bbec9ffbd5990b8311215f53")

# Configurações do servidor FastHTML
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))

# Configurações de segurança
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "c4d61c27a742917ed6d84e28110f2837")