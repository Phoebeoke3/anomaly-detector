"""
Utility functions and scripts for the Anomaly Detection System.

This package contains various utility scripts for:
- Database operations and inspection
- Data visualization and analysis
- Kaggle dataset setup and management
- Wind turbine dataset handling
- System monitoring and reporting
"""

__version__ = "1.0.0"
__author__ = "Anomaly Detection Team"

# Import main utility functions for easy access
from .check_db import check_database_connection, view_table_data
from .view_data_samples import view_data_samples
from .view_table_data import view_table_data
from .setup_kaggle import setup_kaggle_auth, download_wind_turbine_dataset
from .wind_turbine_datasets import WindTurbineDataLoader
from .data_storage_report import generate_storage_report

__all__ = [
    'check_database_connection',
    'view_table_data', 
    'view_data_samples',
    'setup_kaggle_auth',
    'download_wind_turbine_dataset',
    'WindTurbineDataLoader',
    'generate_storage_report'
] 