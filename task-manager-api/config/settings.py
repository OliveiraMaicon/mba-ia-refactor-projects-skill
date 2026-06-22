import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///tasks.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '5000'))

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
