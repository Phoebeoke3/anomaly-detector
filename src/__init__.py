"""
Anomaly Detection System for Wind Turbine Component Manufacturing
A real-time anomaly detection system using MVC architecture.
"""

__version__ = "1.0.0"
__author__ = "Development Team"

# Import main components for easy access
from .models import SensorModel, AnomalyModel, DatabaseModel
from .controllers import APIController, DashboardController

__all__ = [
    'SensorModel', 
    'AnomalyModel', 
    'DatabaseModel',
    'APIController', 
    'DashboardController'
] 