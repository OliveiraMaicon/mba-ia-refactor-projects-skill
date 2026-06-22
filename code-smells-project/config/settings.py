import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
DATABASE_PATH = os.getenv('DATABASE_PATH', 'loja.db')
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '5000'))
