#!/usr/bin/env python3
"""
Launcher script for the Anomaly Detection API Server
Run this from the project root directory.
"""

import sys
import os

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.controllers.api_controller import APIController

if __name__ == "__main__":
    print("Starting Anomaly Detection API Server...")
    print("API will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    app = APIController().create_app()
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False) 