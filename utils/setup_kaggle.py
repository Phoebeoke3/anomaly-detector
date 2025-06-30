#!/usr/bin/env python3
"""
Kaggle Setup and Wind Turbine Dataset Download
Helps set up Kaggle authentication and download wind turbine datasets.
"""

import os
import json
import subprocess
import sys

def check_kaggle_auth():
    """Check if Kaggle authentication is set up."""
    kaggle_path = os.path.expanduser('~/.kaggle/kaggle.json')
    
    if os.path.exists(kaggle_path):
        try:
            with open(kaggle_path, 'r') as f:
                credentials = json.load(f)
                if 'username' in credentials and 'key' in credentials:
                    print(" Kaggle authentication found!")
                    return True
        except Exception as e:
            print(f" Error reading Kaggle credentials: {e}")
    
    return False

def setup_kaggle_auth():
    """Guide user through Kaggle authentication setup."""
    print(" KAGGLE AUTHENTICATION SETUP")
    print("=" * 50)
    
    print("\n To set up Kaggle authentication, follow these steps:")
    print("1. Go to https://www.kaggle.com and sign in")
    print("2. Click on your profile picture → 'Account'")
    print("3. Scroll to 'API' section")
    print("4. Click 'Create New API Token'")
    print("5. This will download a kaggle.json file")
    print("6. Place the kaggle.json file in your .kaggle folder")
    
    kaggle_dir = os.path.expanduser('~/.kaggle')
    print(f"\n Your .kaggle folder location: {kaggle_dir}")
    
    # Create directory if it doesn't exist
    os.makedirs(kaggle_dir, exist_ok=True)
    
    print(f"\n Expected file: {os.path.join(kaggle_dir, 'kaggle.json')}")
    print("\nThe kaggle.json file should contain:")
    print('''
{
  "username": "your_kaggle_username",
  "key": "your_kaggle_api_key"
}
''')
    
    input("\nPress Enter when you have placed the kaggle.json file in the .kaggle folder...")
    
    if check_kaggle_auth():
        print(" Authentication successful!")
        return True
    else:
        print(" Authentication failed. Please check your kaggle.json file.")
        return False

def download_wind_turbine_dataset():
    """Download the wind turbine SCADA dataset."""
    print("\n  DOWNLOADING WIND TURBINE DATASET")
    print("=" * 50)
    
    dataset_name = "berker/wind-turbine-scada-dataset"
    
    try:
        # Create data directory
        os.makedirs('data/kaggle', exist_ok=True)
        
        print(f" Downloading {dataset_name}...")
        
        # Download dataset
        result = subprocess.run([
            'kaggle', 'datasets', 'download',
            '--dataset', dataset_name,
            '--path', 'data/kaggle',
            '--unzip'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(" Dataset downloaded successfully!")
            
            # List downloaded files
            kaggle_dir = 'data/kaggle'
            if os.path.exists(kaggle_dir):
                files = os.listdir(kaggle_dir)
                print(f"\n Downloaded files:")
                for file in files:
                    print(f"   - {file}")
            
            return True
        else:
            print(f" Error downloading dataset:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print(" Kaggle CLI not found. Please install it first:")
        print("   pip install kaggle")
        return False
    except Exception as e:
        print(f" Error: {e}")
        return False

def generate_synthetic_fallback():
    """Generate synthetic wind turbine data as fallback."""
    print("\n🔧 GENERATING SYNTHETIC WIND TURBINE DATA")
    print("=" * 50)
    
    try:
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        # Generate realistic wind turbine manufacturing data
        n_samples = 1000
        np.random.seed(42)
        
        timestamps = pd.date_range(
            start=datetime.now() - timedelta(hours=n_samples),
            periods=n_samples,
            freq='h'
        )
        
        data = pd.DataFrame({
            'timestamp': timestamps,
            'production_line': 'turbine-line-1',
            'component_id': 'blade-1',
            'temperature': np.random.normal(25, 5, n_samples).clip(10, 40),
            'humidity': np.random.normal(50, 15, n_samples).clip(20, 80),
            'sound_level': np.random.normal(65, 10, n_samples).clip(40, 90),
            'target': np.random.choice([0, 1], size=n_samples, p=[0.9, 0.1])
        })
        
        # Add realistic anomalies
        anomaly_indices = np.random.choice(n_samples, size=int(n_samples * 0.1), replace=False)
        data.loc[anomaly_indices, 'temperature'] = np.random.uniform(35, 45, len(anomaly_indices))
        data.loc[anomaly_indices, 'humidity'] = np.random.uniform(80, 95, len(anomaly_indices))
        data.loc[anomaly_indices, 'sound_level'] = np.random.uniform(90, 110, len(anomaly_indices))
        data.loc[anomaly_indices, 'target'] = 1
        
        # Save to CSV
        output_path = 'data/wind_turbine_synthetic.csv'
        os.makedirs('data', exist_ok=True)
        data.to_csv(output_path, index=False)
        print(f" Generated synthetic data saved to: {output_path}")
        print(f" Generated {n_samples} records with 10% anomaly rate")
        
        return True
        
    except Exception as e:
        print(f" Error generating synthetic data: {e}")
        return False

def main():
    """Main function."""
    print("🌪️  WIND TURBINE DATASET SETUP")
    print("=" * 60)
    
    # Check if Kaggle is authenticated
    if not check_kaggle_auth():
        print(" Kaggle authentication not found.")
        if not setup_kaggle_auth():
            print("\n Falling back to synthetic data generation...")
            if generate_synthetic_fallback():
                print("\n Setup complete! You can now use synthetic wind turbine data.")
            return
    
    # Try to download the dataset
    if download_wind_turbine_dataset():
        print("\n Setup complete! Wind turbine dataset downloaded successfully.")
    else:
        print("\n Falling back to synthetic data generation...")
        if generate_synthetic_fallback():
            print("\n Setup complete! You can now use synthetic wind turbine data.")

if __name__ == "__main__":
    main() 