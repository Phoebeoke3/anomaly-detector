# Anomaly Detection System for Wind Turbine Component Manufacturing

A real-time anomaly detection system for wind turbine component manufacturing facilities, featuring sensor data monitoring, machine learning-based anomaly detection, and an interactive dashboard for factory managers and shop floor employees.

## System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Data Ingestion │     │  Data Processing│     │  Model Service  │
│  Layer          │────▶│  Layer          │────▶│  Layer          │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                        │
        │                       │                        │
        ▼                       ▼                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Sensor Data    │     │  Feature        │     │  REST API       │
│  Generator      │     │  Engineering    │     │  Endpoints      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │  Dashboard      │
                                                │  UI             │
                                                └─────────────────┘
```

### Component Details

1. **Data Ingestion Layer**
   - Simulated sensor data generation for wind turbine components
   - Continuous data stream simulation
   - Data validation and preprocessing
   - Real-time data buffering

2. **Data Processing Layer**
   - Feature extraction and normalization
   - Data quality checks
   - Time-series data handling
   - Data persistence (SQLite database)

3. **Model Service Layer**
   - Isolation Forest-based anomaly detection
   - Model training and evaluation
   - Real-time prediction service
   - Model versioning and persistence

4. **API Layer**
   - RESTful endpoints for predictions
   - Health monitoring
   - Model status reporting
   - Data ingestion endpoints

5. **Dashboard Layer**
   - Real-time visualization
   - System status monitoring
   - Historical data analysis
   - Alert management

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

2. Start the dashboard:
```bash
python src/dashboard/app.py
```

3. **Start the simulator in a new terminal (required for live data):**
```bash
python -m src.data.simulator
```

4. Access the dashboard:
Open your web browser and navigate to `http://localhost:5000`

<!-- #,# Troubleshooting

- **Blank charts?**
  - Make sure the simulator is running and sending data.
  - Check the debug endpoint: [http://localhost:5000/api/debug-sensor-count](http://localhost:5000/api/debug-sensor-count)
    - If `count` is 0, the database is empty. Check the simulator output for errors.
  - The simulator and API must use the `sound_level` field (not `sound`).
  - If you see `Error sending data: 400` in the simulator, check that the field names match the API requirements.
  - Ensure Chart.js can access the canvas elements (check browser console for errors). -->

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
