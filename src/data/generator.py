import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import requests
import io
from pathlib import Path
import os
import sqlite3
try:
    from .company_profile import COMPANY_PROFILE
except ImportError:
    from company_profile import COMPANY_PROFILE

class KaggleDataLoader:
    """Loader for semiconductor manufacturing data from Kaggle."""
    
    def __init__(self, dataset_name="uciml/semiconductor-manufacturing", db_path="data/semiconductor.db"):
        self.dataset_name = dataset_name
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.setup_database()
        self.kaggle_available = False
        self._init_kaggle()
    
    def _init_kaggle(self):
        """Initialize Kaggle API if available."""
        try:
            # Check if kaggle.json exists
            kaggle_path = os.path.expanduser('~/.kaggle/kaggle.json')
            if not os.path.exists(kaggle_path):
                print("\nKaggle credentials not found!")
                print("To use Kaggle datasets, please follow these steps:")
                print("1. Go to https://www.kaggle.com and sign in")
                print("2. Click on your profile picture → 'Account'")
                print("3. Scroll to 'API' section and click 'Create New API Token'")
                print("4. This will download a kaggle.json file")
                print("5. Create a .kaggle folder in your home directory:")
                print("   - Windows: C:\\Users\\<Your-Username>\\.kaggle")
                print("   - Linux/Mac: ~/.kaggle")
                print("6. Move the kaggle.json file to the .kaggle folder")
                print("\nFalling back to synthetic data generation...")
                return

            # Try to import kaggle
            try:
                import kaggle
            except ImportError:
                print("\nKaggle package not installed!")
                print("To use Kaggle datasets, please install the package:")
                print("pip install kaggle")
                print("\nFalling back to synthetic data generation...")
                return

            # Set environment variables for Kaggle API
            os.environ['KAGGLE_CONFIG_DIR'] = os.path.dirname(kaggle_path)
            os.environ['KAGGLE_USERNAME'] = self._get_kaggle_username(kaggle_path)
            os.environ['KAGGLE_KEY'] = self._get_kaggle_key(kaggle_path)
            
            # Now try to authenticate
            try:
                kaggle.api.authenticate()
                self.kaggle_available = True
                print("Kaggle API authenticated successfully!")
            except Exception as e:
                print(f"\nError authenticating with Kaggle: {e}")
                print("Please verify your Kaggle API credentials in kaggle.json")
                print("Falling back to synthetic data generation...")
                
        except Exception as e:
            print(f"\nError initializing Kaggle: {e}")
            print("Falling back to synthetic data generation...")
    
    def _get_kaggle_username(self, kaggle_path):
        """Extract username from kaggle.json."""
        try:
            import json
            with open(kaggle_path, 'r') as f:
                credentials = json.load(f)
                return credentials.get('username', '')
        except Exception:
            return ''
    
    def _get_kaggle_key(self, kaggle_path):
        """Extract API key from kaggle.json."""
        try:
            import json
            with open(kaggle_path, 'r') as f:
                credentials = json.load(f)
                return credentials.get('key', '')
        except Exception:
            return ''
    
    def connect(self):
        """Connect to SQLite database."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Connect to SQLite database
            self.conn = sqlite3.connect(self.db_path)
            print("Connected to SQLite database successfully!")
        except Exception as e:
            print(f"Error connecting to SQLite: {e}")
            print("Falling back to synthetic data...")
            self.conn = None
    
    def setup_database(self):
        """Create table if it doesn't exist."""
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    timestamp DATETIME,
                    production_line TEXT,
                    component_id TEXT,
                    temperature REAL,
                    humidity REAL,
                    sound REAL,
                    is_anomaly INTEGER,
                    PRIMARY KEY (production_line, timestamp, component_id)
                )
            """)
            self.conn.commit()
            print("Database setup complete!")
        except Exception as e:
            print(f"Error setting up database: {e}")
    
    def download_kaggle_data(self):
        """Download data from Kaggle."""
        if not self.kaggle_available:
            return False
            
        try:
            import kaggle
            # Create data directory if it doesn't exist
            os.makedirs('data/kaggle', exist_ok=True)
            
            # Download the dataset with explicit authentication
            kaggle.api.dataset_download_files(
                self.dataset_name,
                path='data/kaggle',
                unzip=True,
                force=True  # Force download even if files exist
            )
            print("Kaggle dataset downloaded successfully!")
            return True
        except Exception as e:
            print(f"Error downloading Kaggle dataset: {e}")
            print("Please verify your Kaggle API credentials and internet connection")
            return False
    
    def load_kaggle_data(self):
        """Load and preprocess Kaggle data."""
        if not self.kaggle_available:
            return None
            
        try:
            # Load the SECOM dataset
            data_path = 'data/kaggle/secom.data'
            labels_path = 'data/kaggle/secom_labels.data'
            
            if not os.path.exists(data_path) or not os.path.exists(labels_path):
                if not self.download_kaggle_data():
                    return None
            
            # Read the data
            data = pd.read_csv(data_path, sep=' ', header=None)
            labels = pd.read_csv(labels_path, sep=' ', header=None)
            
            # Clean the data
            data = data.replace('?', np.nan)
            data = data.astype(float)
            
            # Fill missing values with column means
            data = data.fillna(data.mean())
            
            # Select relevant features (temperature, humidity, sound-like sensors)
            # We'll map the SECOM features to our sensor types
            feature_mapping = {
                'temperature': [0, 1, 2],  # First three features as temperature
                'humidity': [3, 4, 5],     # Next three features as humidity
                'sound': [6, 7, 8]         # Next three features as sound
            }
            
            processed_data = pd.DataFrame()
            processed_data['temperature'] = data.iloc[:, feature_mapping['temperature']].mean(axis=1)
            processed_data['humidity'] = data.iloc[:, feature_mapping['humidity']].mean(axis=1)
            processed_data['sound'] = data.iloc[:, feature_mapping['sound']].mean(axis=1)
            processed_data['target'] = labels.iloc[:, 0]  # Anomaly labels
            
            # Normalize the data to match our expected ranges
            processed_data['temperature'] = self.normalize_to_range(processed_data['temperature'], 20, 30)
            processed_data['humidity'] = self.normalize_to_range(processed_data['humidity'], 40, 60)
            processed_data['sound'] = self.normalize_to_range(processed_data['sound'], 50, 70)
            
            # Add timestamps
            processed_data['timestamp'] = pd.date_range(
                start=datetime.now() - timedelta(days=len(processed_data)),
                periods=len(processed_data),
                freq='h'
            )
            
            # Add production line and component information
            processed_data['production_line'] = 'line-1'
            processed_data['component_id'] = 'wafer-1'
            
            return processed_data
            
        except Exception as e:
            print(f"Error loading Kaggle data: {e}")
            return None
    
    def normalize_to_range(self, series, min_val, max_val):
        """Normalize a series to a specific range."""
        return (series - series.min()) / (series.max() - series.min()) * (max_val - min_val) + min_val
    
    def insert_data(self, data):
        """Insert data into SQLite."""
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor()
            for _, row in data.iterrows():
                cursor.execute("""
                    INSERT OR REPLACE INTO sensor_readings 
                    (timestamp, production_line, component_id, temperature, humidity, sound, is_anomaly)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),  # Convert Timestamp to string
                    row['production_line'],
                    row['component_id'],
                    float(row['temperature']),
                    float(row['humidity']),
                    float(row['sound']),
                    int(row['target'])
                ))
            self.conn.commit()
            print("Data inserted successfully!")
        except Exception as e:
            print(f"Error inserting data: {e}")
    
    def get_latest_data(self, production_line, limit=100):
        """Get latest sensor readings from SQLite."""
        if not self.conn:
            return self.generate_synthetic_data(limit)
            
        try:
            query = """
                SELECT * FROM sensor_readings
                WHERE production_line = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            df = pd.read_sql_query(
                query, 
                self.conn, 
                params=(production_line, limit),
                parse_dates=['timestamp']
            )
            return df
        except Exception as e:
            print(f"Error retrieving data: {e}")
            return self.generate_synthetic_data(limit)
    
    def generate_synthetic_data(self, n_samples=1000):
        """Generate synthetic data as fallback for wind turbine component factory."""
        print("Generating synthetic wind turbine factory data as fallback...")
        np.random.seed(42)
        
        # Generate timestamps
        timestamps = pd.date_range(
            start=datetime.now() - timedelta(hours=n_samples),
            periods=n_samples,
            freq='h'
        )
        
        # Generate sensor data for wind turbine context
        data = pd.DataFrame({
            'timestamp': timestamps,
            'production_line': 'turbine-line-1',
            'component_id': 'blade-1',
            'temperature': np.random.normal(25, 5, n_samples).clip(10, 40),
            'humidity': np.random.normal(50, 15, n_samples).clip(20, 80),
            'sound': np.random.normal(65, 10, n_samples).clip(40, 90),
            'target': np.random.choice([0, 1], size=n_samples, p=[0.9, 0.1])
        })
        
        return data

class SensorDataGenerator:
    """Main class for generating wind turbine sensor data."""
    
    def __init__(self):
        self.loader = KaggleDataLoader()
        self.data = self.loader.load_kaggle_data()
        if self.data is not None:
            self.loader.insert_data(self.data)
    
    def generate_mixed_data(self, n_samples=1000, anomaly_ratio=0.1):
        """Generate a mix of normal and anomalous wind turbine data."""
        if self.data is not None:
            samples = self.data.sample(n=min(n_samples, len(self.data)))
            return samples
        else:
            return self.loader.generate_synthetic_data(n_samples)
    
    def generate_normal_data(self, n_samples=1000):
        """Generate only normal wind turbine data."""
        if self.data is not None:
            normal_data = self.data[self.data['target'] == 0]
            samples = normal_data.sample(n=min(n_samples, len(normal_data)))
            return samples
        else:
            data = self.loader.generate_synthetic_data(n_samples)
            data['target'] = 0
            return data 