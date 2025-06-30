# Anomaly Detection System for Wind Turbine Component Manufacturing

A real-time anomaly detection system for wind turbine component manufacturing facilities, featuring sensor data monitoring, machine learning-based anomaly detection, and an interactive dashboard for factory managers and shop floor employees.

## System Architecture

```
flowchart LR
    A[Sensor Data (Simulated)] -->|Stream| B[Data Ingestion Script]
    B --> C[Data Storage (SQLite)]
    B --> D[Anomaly Detection API (Flask)]
    D --> E[Dashboard]
    D --> F[Monitoring & Logging]
    E -->|User Feedback| D
```

- **Sensor Data**: Simulated wind turbine sensor data (temperature, humidity, sound).
- **Data Ingestion**: Python script generates and POSTs data to the API.
- **Data Storage**: SQLite database for persistence.
- **Anomaly Detection API**: Flask app, receives sensor data, returns anomaly score.
- **Dashboard**: Visualizes production line status, sensor trends, and anomalies.
- **Monitoring & Logging**: Logs all API requests, predictions, and errors. `/api/health` endpoint for health checks.

## Data Source and Simulation

The system uses simulated sensor data that mimics real wind turbine component manufacturing conditions:

1. **Data Generation**
   - Temperature: 10-40°C (normal range for blade production)
   - Humidity: 20-80% (normal range for resin curing)
   - Sound Level: 40-90 dB (normal range for assembly operations)
   - Anomaly injection for testing

2. **Data Stream Simulation**
   - Continuous data generation
   - Configurable update frequency (1 second intervals)
   - Realistic noise and patterns
   - Anomaly scenarios simulation

## Features

- Real-time monitoring of wind turbine component manufacturing processes
- Machine learning-based anomaly detection using Isolation Forest
- Interactive dashboard with live sensor data visualization
- Multiple production line monitoring (Blade Production, Nacelle Assembly)
- Configurable sensor thresholds
- Historical data tracking (24-hour data retention)
- System health monitoring
- Live anomaly score distribution and trends

## Project Structure

```
.
├── config/
│   └── company_config.json    # Company and facility configuration
├── src/
│   ├── data/
│   │   ├── generator.py      # Sensor data generation
│   │   ├── simulator.py      # Data simulator for live streaming
│   │   └── sqlite_db.py      # Database operations
│   ├── model/
│   │   └── train.py         # Model training and prediction
│   └── dashboard/
│       ├── app.py           # Flask application
│       └── templates/
│           └── index.html   # Dashboard UI
├── utils/                    # Utility scripts and functions
│   ├── __init__.py          # Package initialization
│   ├── README.md            # Utils documentation
│   ├── check_db.py          # Database connection testing
│   ├── view_data_samples.py # Data visualization utilities
│   ├── view_table_data.py   # Table data inspection
│   ├── setup_kaggle.py      # Kaggle dataset setup
│   ├── wind_turbine_datasets.py # Dataset handling
│   └── data_storage_report.py   # Storage analysis
├── models/                   # Trained model storage
├── requirements.txt         # Project dependencies
└── README.md               # Project documentation
```

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd anomaly-detection
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Train the anomaly detection model:
```bash
python src/model/train.py
```

2. Start the API server (port 5000):
```bash
python run_api.py
```

3. Start the dashboard server (port 5001):
```bash
python run_dashboard.py
```

4. **Start the simulator in a new terminal (required for live data):**
```bash
python -m src.data.simulator
```

5. Access the dashboard:
Open your web browser and navigate to `http://localhost:5001`

## View all data
python utils/view_data_samples.py

# Or use the existing viewer for specific tables
python utils/view_table_data.py

# View specific table with custom limit
python -c "from utils.view_table_data import view_table_data; view_table_data('sensor_readings', 50)"

# Check database connection
python utils/check_db.py

# Setup Kaggle datasets
python utils/setup_kaggle.py

## Debug Endpoints

- `/api/debug-sensor-count`: Returns the number of sensor readings and timestamp range in the database. Useful for diagnosing data flow issues.

## API Endpoints

- `POST /api/predict`: Submit sensor data for anomaly detection
- `GET /api/current-status`: Get current system status
- `GET /api/production-lines`: Get production line status
- `GET /api/sensor-history/<sensor_type>`: Get historical sensor data (temperature, humidity, sound_level)
- `GET /api/thresholds`: Get current anomaly detection thresholds

## Dashboard Features

- **System Status**: Shows the current status of the anomaly detection model and system health
- **Production Lines**: Real-time monitoring of wind turbine production lines (Blade Production, Nacelle Assembly)
- **Sensor Data**: Live visualization of temperature, humidity, and sound level data with historical trends
- **Anomaly Analysis**: Real-time anomaly score distribution and historical trends
- **Sensor Correlation**: Radar chart showing relationships between different sensors

## Configuration

The system can be configured through `config/company_config.json`:

- Company information
- Production line details
- Sensor configurations
- Threshold values for anomaly detection

Example configuration:
```json
{
    "name": "PTech",
    "facility": "Wind Turbine Manufacturing Plant",
    "production_lines": [
        {
            "id": "turbine-line-1",
            "name": "Blade Production Line",
            "components": ["Blade", "Resin Infusion", "Curing Oven"],
            "sensors": ["temperature", "humidity", "sound_level"]
        },
        {
            "id": "turbine-line-2",
            "name": "Nacelle Assembly Line",
            "components": ["Nacelle", "Gearbox", "Generator"],
            "sensors": ["temperature", "humidity", "sound_level"]
        }
    ],
    "sensor_thresholds": {
        "temperature": {
            "min": 10,
            "max": 40,
            "warning": 30
        },
        "humidity": {
            "min": 20,
            "max": 80,
            "warning": 60
        },
        "sound_level": {
            "min": 40,
            "max": 90,
            "warning": 70
        }
    }
}
```

## Dependencies

- Flask 2.0.1: Web framework for the dashboard
- NumPy 1.21.0: Numerical computing
- Pandas 1.3.0: Data manipulation
- scikit-learn 0.24.2: Machine learning algorithms
- joblib 1.0.1: Model persistence
- Chart.js: Interactive charts and visualizations
- Bootstrap: Responsive UI framework

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the development team.

Python 3.7+
├── Flask>=2.0.1          # Web framework
├── numpy>=1.21.0         # Numerical computing
├── pandas>=1.3.0         # Data manipulation
├── scikit-learn>=0.24.2  # Machine learning
├── joblib>=1.0.1         # Model persistence
├── requests>=2.25.1      # HTTP client
├── python-dotenv>=0.19.0 # Environment management
└── kaggle>=1.7.4.5       # Kaggle API

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Model Configuration for Wind Turbine Context
model = IsolationForest(
    contamination=0.1,      # Expected 10% anomaly rate in manufacturing
    random_state=42,
    n_estimators=100
)

# Feature Engineering for Wind Turbine Sensors
scaler = StandardScaler()
features = ['temperature', 'humidity', 'sound_level']

# Real-time wind turbine sensor data generator
class DataSimulator:
    def run(self, duration=None):
        while True:
            # Generate realistic wind turbine manufacturing data
            data = {
                "temperature": random.uniform(10, 40),  # Blade curing range
                "humidity": random.uniform(20, 80),     # Resin infusion range
                "sound_level": random.uniform(40, 90),  # Assembly operations
                "timestamp": datetime.now().isoformat(),
                "sensor_id": "simulator-1",
                "production_line": "turbine-line-1"
            }
            
            # HTTP POST to API endpoint every 1 second
            requests.post("http://localhost:5000/api/predict", json=data)
            time.sleep(1.0)

from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

@app.route('/api/predict', methods=['POST'])
def predict_anomaly():
    # 1. Receive wind turbine sensor data
    data = request.get_json()
    
    # 2. Validate manufacturing ranges
    validate_wind_turbine_data(data)
    
    # 3. Create DataFrame for prediction
    df = pd.DataFrame([{
        'temperature': data['temperature'],
        'humidity': data['humidity'],
        'sound_level': data['sound_level']
    }])
    
    # 4. Feature engineering and prediction
    features = scaler.transform(df[features])
    anomaly_score = model.predict(features)[0]
    
    # 5. Return standardized response
    return jsonify({
        'anomaly_score': float(anomaly_score),
        'status': classify_manufacturing_status(anomaly_score),
        'timestamp': data['timestamp'],
        'production_line': data['production_line']
    })

## How to Run the System

### 1. Train the Model
```
python src/model/train.py
```

### 2. Start the API Server
```
python run_api.py
```

### 3. Start the Data Simulator
```
python utils/simulate_wind_turbine_data.py
```

### 4. Open the Dashboard
- Visit [http://localhost:5001/](http://localhost:5001/) in your browser (or the port your API is running on).

## Monitoring & Logging
- All API requests, responses, and errors are logged to `app.log`.
- Check system health at [http://localhost:5001/api/health](http://localhost:5001/api/health) (update port if needed).

## Troubleshooting

### 404 Errors from the Simulator
- If you see `[ERR] 404: ... Not Found` from the simulator, it means the API endpoint is not available at the specified URL.
- **Check which port your API server is running on.**
  - When you start the API, look for a line like `Running on http://127.0.0.1:5000` or `http://127.0.0.1:5001`.
- **Update the simulator's `API_URL`** in `utils/simulate_wind_turbine_data.py` to match the port:
  ```python
  API_URL = 'http://localhost:5000/api/predict'  # or 5001, as needed
  ```
- **Ensure `/api/predict` is defined** in your running Flask app.
- **Restart both the API server and the simulator** after making changes.

### Other Issues
- If the dashboard is blank or spinning, check the browser console and network tab for errors.
- Make sure the simulator is running and populating the database.
- Check `app.log` for backend errors.

## Notes
- The system uses only wind turbine sensor data (no SECOM or external datasets).
- The dashboard always shows all production lines from the config.
- The anomaly detection model is simple and easily replaceable.
- The system is designed for easy monitoring, maintainability, and extensibility.
