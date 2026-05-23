import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    _db_url = os.environ.get('DATABASE_URL', 'postgresql://localhost/traveloop')
    SQLALCHEMY_DATABASE_URI = _db_url.replace('postgresql://', 'postgresql+pg8000://', 1).replace('postgres://', 'postgresql+pg8000://', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    MAIL_USERNAME  = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD  = os.environ.get('MAIL_PASSWORD', '')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GROQ_API_KEY   = os.environ.get('GROQ_API_KEY', '')
