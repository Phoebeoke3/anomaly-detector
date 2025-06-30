#!/usr/bin/env python3
"""
Launcher script for the Anomaly Detection Dashboard
Run this from the project root directory.
"""

import sys
import os

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.controllers.dashboard_controller import DashboardController

if __name__ == "__main__":
    print("Starting Anomaly Detection Dashboard...")
    print("Dashboard will be available at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    
    app = DashboardController().create_app()
    app.run(debug=True, port=5001, host='0.0.0.0') 