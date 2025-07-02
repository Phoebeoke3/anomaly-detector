# Anomaly Detection System for Wind Turbine Component Manufacturing

A real-time anomaly detection system for wind turbine component manufacturing facilities, featuring sensor data monitoring, machine learning-based anomaly detection, and an interactive dashboard for factory managers and shop floor employees.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the API server:**
   ```bash
   python -m utils.run_api
   ```

3. **Start the dashboard:**
   ```bash
   python -m utils.run_dashboard
   ```

4. **Start the data simulator (in a new terminal):**
   ```bash
   python -m utils.simulate_wind_turbine_data
   ```

5. **Access the dashboard:**
   Open your browser and go to `http://localhost:5001`


- **Sensor Data**: Simulated wind turbine sensor data (temperature, humidity, sound)
- **Data Ingestion**: Python script generates and POSTs data to the API
- **Data Storage**: SQLite database for persistence
- **Anomaly Detection API**: Flask app that receives sensor data and returns anomaly scores
- **Dashboard**: Interactive web interface for monitoring production lines and sensor data
- **Monitoring & Logging**: Comprehensive logging of all API requests, predictions, and errors

## Features

### Core Functionality
- **Real-time monitoring** of wind turbine component manufacturing processes
- **Machine learning-based anomaly detection** using Isolation Forest algorithm
- **Interactive dashboard** with live sensor data visualization
- **Multiple production line monitoring** (Blade Production, Nacelle Assembly)
- **Configurable sensor thresholds** for different manufacturing conditions
- **Historical data tracking** with 24-hour data retention
- **System health monitoring** with health check endpoints

### Dashboard Features
- **System Status**: Real-time status of anomaly detection model and system health
- **Production Lines**: Live monitoring of wind turbine production lines with status indicators
- **Sensor Data**: Real-time visualization of temperature, humidity, and sound level data
- **Anomaly Analysis**: Live anomaly score distribution and historical trends
- **System Statistics**: Total production lines, normal/warning/critical status counts, and average anomaly scores
- **Data Export**: CSV export functionality for data analysis
- **Responsive Design**: Works on desktop and mobile devices

### Technical Features
- **RESTful API** with comprehensive endpoints
- **Real-time data streaming** with configurable update frequency
- **Database persistence** with SQLite for reliable data storage
- **Model versioning** with automatic model saving and loading
- **Error handling** with detailed logging and debugging endpoints

## Project Structure

```
Anomaly detection/
├── config/
│   └── company_config.json          # Company and facility configuration
├── data/
│   ├── cache/                       # Cached datasets
│   ├── kaggle/                      # Kaggle datasets
│   ├── wind_turbine_synthetic.csv   # Synthetic wind turbine data
│   └── wind_turbine.db              # SQLite database
├── docs/
│   ├── architecture.md              # System architecture documentation
│   └── streaming_architecture.md    # Data streaming documentation
├── models/                          # Trained model storage
├── src/
│   ├── api/
│   │   ├── app.py                   # API Flask application
│   │   └── main.py                  # API entry point
│   ├── controllers/
│   │   ├── api_controller.py        # API request handling
│   │   └── dashboard_controller.py  # Dashboard request handling
│   ├── dashboard/
│   │   ├── app.py                   # Dashboard Flask application
│   │   └── main.py                  # Dashboard entry point
│   ├── data/
│   │   ├── company_profile.py       # Company configuration handling
│   │   ├── generator.py             # Sensor data generation
│   │   ├── simulator.py             # Data simulator for live streaming
│   │   └── sqlite_db.py             # Database operations
│   ├── model/
│   │   └── train.py                 # Model training and prediction
│   ├── models/
│   │   ├── anomaly_model.py         # Anomaly detection model
│   │   ├── database_model.py        # Database model operations
│   │   └── sensor_model.py          # Sensor data model
│   └── views/
│       ├── static/                  # CSS, JS, and static assets
│       └── templates/
│           ├── data_view.html       # Data visualization page
│           ├── index.html           # Main dashboard
│           └── predictions.html     # Predictions page
├── utils/
│   ├── check_sensor_data.py         # Sensor data validation
│   ├── run_api.py                   # API server runner
│   ├── run_dashboard.py             # Dashboard server runner
│   ├── setup_kaggle.py              # Kaggle dataset setup
│   └── simulate_wind_turbine_data.py # Data simulation runner
├── app.log                          # Application logs
├── requirements.txt                 # Python dependencies
└── README.md                        # Project documentation
```

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <https://github.com/Phoebeoke3/anomaly-detector>
   cd anomaly-detection
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the System

1. **Start the API server (port 5000):**
   ```bash
   python -m utils.run_api
   ```

2. **Start the dashboard server (port 5001):**
   ```bash
   python -m utils.run_dashboard
   ```

3. **Start the data simulator (in a new terminal):**
   ```bash
   python -m utils.simulate_wind_turbine_data
   ```

4. **Access the dashboard:**
   Open your web browser and navigate to `http://localhost:5001`

### Data Management

- **View data samples:**
  ```bash
  python utils/view_data_samples.py
  ```

- **View specific table data:**
  ```bash
  python utils/view_table_data.py
  ```

- **Check database connection:**
  ```bash
  python utils/check_db.py
  ```

- **Setup Kaggle datasets:**
  ```bash
  python utils/setup_kaggle.py
  ```

## API Endpoints

### Core Endpoints
- `POST /api/predict` - Submit sensor data for anomaly detection
- `GET /api/current-status` - Get current system status and production line information
- `GET /api/production-lines` - Get production line status
- `GET /api/sensor-history/<sensor_type>` - Get historical sensor data
- `GET /api/thresholds` - Get current anomaly detection thresholds
- `GET /api/data-samples` - Get sample data from database
- `GET /api/table-data/<table_name>` - Get data from specific database table

### Debug Endpoints
- `GET /api/debug-sensor-count` - Returns sensor count and timestamp range
- `GET /api/health` - System health check

### Dashboard Endpoints
- `GET /` - Main dashboard page
- `GET /predictions` - Predictions page
- `GET /api/dashboard-data` - Dashboard data API
- `GET /export-csv` - Export data as CSV


## Data Source and Simulation

The system uses simulated sensor data that mimics real wind turbine component manufacturing conditions:

### Data Generation Parameters
- **Temperature**: 10-40°C (normal range for blade production)
- **Humidity**: 20-80% (normal range for resin curing)
- **Sound Level**: 40-90 dB (normal range for assembly operations)

### Data Stream Features
- Continuous data generation with 1-second intervals
- Realistic noise and patterns
- Anomaly injection for testing
- Multiple production line simulation

## Dependencies

### Core Dependencies
- **Flask 2.0.1** - Web framework for API and dashboard
- **NumPy 1.21.0** - Numerical computing
- **Pandas 1.3.0** - Data manipulation and analysis
- **scikit-learn 0.24.2** - Machine learning algorithms
- **joblib 1.0.1** - Model persistence
- **requests 2.25.1** - HTTP client for API calls
- **python-dotenv 0.19.0** - Environment management

### Frontend Dependencies
- **Chart.js** - Interactive charts and visualizations
- **Bootstrap** - Responsive UI framework
- **jQuery** - JavaScript library for DOM manipulation

## Troubleshooting

### Common Issues

1. **Dashboard not loading or showing errors:**
   - Ensure both API and dashboard servers are running
   - Check browser console for JavaScript errors
   - Verify the correct template is being served

2. **No data appearing in dashboard:**
   - Make sure the data simulator is running
   - Check database connection and data insertion
   - Verify API endpoints are responding correctly

3. **404 errors from simulator:**
   - Check which port your API server is running on
   - Update the simulator's `API_URL` in `utils/simulate_wind_turbine_data.py`
   - Ensure `/api/predict` endpoint is available

4. **System status stuck loading:**
   - Check API response format
   - Verify all required fields are present in API responses
   - Check browser network tab for failed requests

### Debug Steps

1. **Check server logs:**
   - Monitor `app.log` for backend errors
   - Check terminal output for server errors

2. **Verify API endpoints:**
   - Test `/api/health` endpoint
   - Check `/api/current-status` response format

3. **Database issues:**
   - Run `python utils/check_db.py` to verify database connection
   - Check if data is being inserted correctly

4. **Model issues:**
   - Verify model files exist in `models/` directory
   - Check model loading in anomaly detection code

## Monitoring & Logging

- **Application logs**: All API requests, responses, and errors are logged to `app.log`
- **System health**: Check system health at `/api/health` endpoint
- **Database monitoring**: Use debug endpoints to monitor data flow
- **Performance monitoring**: Track API response times and system performance

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the troubleshooting section above
2. Review the logs in `app.log`
3. Open an issue in the repository
4. Contact the development team

