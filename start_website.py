#!/usr/bin/env python3
"""
Face Matching Gateway Website Launcher
Quick script to start the FastAPI server with the web interface
"""

import os
import sys
import subprocess
from pathlib import Path
from app.core.config import APP_HOST, APP_PORT

def check_requirements():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import onnxruntime
        print("All required packages are installed")
        return True
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    if not Path('.env').exists():
        print(" .env file not found. Using default host/port from app/core/config.py.")
        print("If you want to override settings, create a .env file with your configuration:")
        print("""
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
ADMIN_API_KEY=your-admin-api-key
TRITON_SERVER_URL=localhost:8001
APP_HOST=127.0.0.1
APP_PORT=8000
        """)
        return True
    print(" .env file found")
    return True

def start_server(host="127.0.0.1", port=8080):
    """Start the FastAPI server"""
    print(f"Starting Face Matching Gateway server...")
    print(f"Website will be available at: http://{host}:{port}/web")
    print(f"API documentation at: http://{host}:{port}/docs")
    print(f"Press Ctrl+C to stop the server")
    print("-" * 50)

    try:
        # Run uvicorn server
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--reload",
            "--host", host,
            "--port", str(port)
        ]

        subprocess.run(cmd, check=True)

    except KeyboardInterrupt:
        print("\n Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f" Failed to start server: {e}")
        return False

    return True

def main():
    print(" Face Matching Gateway - Website Launcher")
    print("=" * 50)

    # Check requirements
    if not check_requirements():
        return

    # Check environment
    if not check_env_file():
        return

    host = APP_HOST or "127.0.0.1"
    port_value = APP_PORT or "8080"
    try:
        port = int(port_value) if port_value else APP_PORT
    except ValueError:
        port = APP_PORT

    print(f"Using host={host}, port={port}")
    start_server(host, port)

if __name__ == "__main__":
    main()