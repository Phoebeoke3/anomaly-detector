import time
import requests
import json
from datetime import datetime
from .generator import SensorDataGenerator
import sqlite3

class DataSimulator:
    def __init__(self, api_url="http://localhost:5000/api/predict", interval=1.0):
        """Initialize the data simulator."""
        self.api_url = api_url
        self.interval = interval
        self.generator = SensorDataGenerator()
        
    def send_data(self, data):
        """Send data to the API endpoint."""
        try:
            # Rename 'sound' to 'sound_level' for API compatibility
            data = data.rename(columns={'sound': 'sound_level'})
            # Convert timestamp to string for JSON serialization
            data_dict = data.to_dict('records')[0]
            data_dict['timestamp'] = data_dict['timestamp'].isoformat()
            response = requests.post(
                self.api_url,
                json=data_dict,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Data sent successfully. Anomaly score: {result['anomaly_score']:.4f}")
            else:
                print(f"Error sending data: {response.status_code}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def run(self, duration=None):
        """Run the simulator for a specified duration or indefinitely."""
        print("Starting data simulator...")
        start_time = time.time()
        
        try:
            while True:
                # Generate a single data point
                data = self.generator.generate_mixed_data(n_samples=1, anomaly_ratio=0.1)
                
                # Send the data
                self.send_data(data)
                
                # Check if we should stop
                if duration and (time.time() - start_time) > duration:
                    break
                    
                # Wait for the next interval
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\nSimulator stopped by user")
        except Exception as e:
            print(f"Simulator stopped due to error: {str(e)}")

if __name__ == "__main__":
    simulator = DataSimulator()
    simulator.run() 