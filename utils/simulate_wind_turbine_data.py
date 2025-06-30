import time
import random
import requests
import json

CONFIG_PATH = 'config/company_config.json'
API_URL = 'http://localhost:5000/api/predict'

# Load production lines from config
with open(CONFIG_PATH, 'r') as f:
    company = json.load(f)
lines = company.get('production_lines', [])

# Sensor value ranges (realistic for wind turbine factory)
TEMP_RANGE = (15, 40)
HUMIDITY_RANGE = (20, 80)
SOUND_RANGE = (40, 90)

print('Starting wind turbine data simulation...')

while True:
    for line in lines:
        data = {
            'production_line': line['id'],
            'component_id': line['components'][0],
            'temperature': round(random.uniform(*TEMP_RANGE), 2),
            'humidity': round(random.uniform(*HUMIDITY_RANGE), 2),
            'sound_level': round(random.uniform(*SOUND_RANGE), 2),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        try:
            response = requests.post(API_URL, json=data)
            if response.status_code == 200:
                print(f"[OK] {data['production_line']} {data['component_id']} -> {response.json()['anomaly_score']}")
            else:
                print(f"[ERR] {response.status_code}: {response.text}")
        except Exception as e:
            print(f"[EXC] {e}")
    time.sleep(2)  # Wait 2 seconds before next round 