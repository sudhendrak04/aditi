#!/usr/bin/env python3
"""
KJSIT Book Recommendation System - Startup Script
This script initializes the database, seeds sample data, and starts the application.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def print_banner():
    """Print application banner"""
    banner = """
    📚 KJSIT Book Recommendation System
    ===================================

    An intelligent book recommendation system for KJSIT students
    Built with Streamlit, Python, and Machine Learning
    """
    print(banner)

def check_requirements():
    """Check if required packages are installed"""
    try:
        import streamlit
        import pandas
        import sklearn
        import plotly
        import sqlalchemy
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def initialize_database():
    """Initialize database and seed sample data"""
    print("🔧 Initializing database...")
    try:
        from seed_data import seed_sample_data
        seed_sample_data()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def start_application(port=8501):
    """Start the Streamlit application"""
    print(f"🚀 Starting application on port {port}...")
    try:
        cmd = [sys.executable, "-m", "streamlit", "run", "app.py",
               "--server.port", str(port),
               "--server.address", "0.0.0.0"]

        if not os.getenv('DEBUG', 'True').lower() == 'true':
            cmd.append("--server.headless")
            cmd.append("true")

        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

def reset_database():
    """Reset database (remove and recreate)"""
    db_path = "books_recommendation.db"
    if os.path.exists(db_path):
        print("🗑️  Removing existing database...")
        os.remove(db_path)

    print("🔄 Creating fresh database...")
    return initialize_database()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='KJSIT Book Recommendation System')
    parser.add_argument('--port', '-p', type=int, default=8501,
                       help='Port to run the application on')
    parser.add_argument('--reset', '-r', action='store_true',
                       help='Reset database before starting')
    parser.add_argument('--init-only', '-i', action='store_true',
                       help='Only initialize database, don\'t start app')

    args = parser.parse_args()

    print_banner()

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Reset database if requested
    if args.reset:
        if not reset_database():
            sys.exit(1)

    # Initialize database if not exists or if reset was requested
    if args.reset:
        # Already initialized during reset_database()
        pass
    elif not os.path.exists("books_recommendation.db"):
        if not initialize_database():
            sys.exit(1)

    # Exit if init-only mode
    if args.init_only:
        print("✅ Database initialized. Exiting...")
        return

    # Start application
    start_application(args.port)

if __name__ == "__main__":
    main()
