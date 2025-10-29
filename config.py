import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///books_recommendation.db')

    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

    # Application
    PORT = int(os.getenv('PORT', 8501))

    # API Keys
    GOOGLE_BOOKS_API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY', '')

    # Recommendation System
    MIN_RATINGS_THRESHOLD = int(os.getenv('MIN_RATINGS_THRESHOLD', 5))
    SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', 0.3))
    MAX_RECOMMENDATIONS = int(os.getenv('MAX_RECOMMENDATIONS', 10))

    # File paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, 'books_recommendation.db')

# Create config instance
config = Config()
