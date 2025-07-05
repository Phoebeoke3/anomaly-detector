# Anomaly Detection System for Wind Turbine Component Manufacturing

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0.1-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A real-time anomaly detection system for wind turbine component manufacturing facilities, featuring sensor data monitoring, machine learning-based anomaly detection, and an interactive dashboard for factory managers and shop floor employees.

## Table of Contents

- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the System](#running-the-system)
- [System Overview](#system-overview)
- [Features](#features)
  - [Core Functionality](#core-functionality)
  - [Dashboard Features](#dashboard-features)
  - [Technical Features](#technical-features)
- [Project Structure](#project-structure)
- [Data Management](#data-management)
  - [Utility Commands](#utility-commands)
- [Advanced Stream Processing](#advanced-stream-processing)
  - [Overview](#overview)
  - [Features](#features-1)
  - [Running Advanced Stream Processing](#running-advanced-stream-processing)
  - [Stream Processing Components](#stream-processing-components)
  - [Configuration Options](#configuration-options)
- [API Endpoints](#api-endpoints)
  - [Core Endpoints](#core-endpoints)
  - [Debug Endpoints](#debug-endpoints)
  - [Dashboard Endpoints](#dashboard-endpoints)
- [Data Source and Simulation](#data-source-and-simulation)
  - [Data Generation Parameters](#data-generation-parameters)
  - [Data Stream Features](#data-stream-features)
- [Dependencies](#dependencies)
  - [Core Dependencies](#core-dependencies)
  - [Frontend Dependencies](#frontend-dependencies)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Debug Steps](#debug-steps)
- [Monitoring & Logging](#monitoring--logging)
- [Contributing](#contributing)
  - [Development Guidelines](#development-guidelines)
- [License](#license)
- [Support](#support)
- [Related Documentation](#related-documentation)
- [Changelog](#changelog)

## Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Phoebeoke3/anomaly-detector
   cd anomaly-detector
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

### Running the System

1. **Start the API server (port 5000):**
   ```bash
   python -m utils.run_api
   ```

2. **Start the dashboard server (port 5001) in a new terminal:**
   ```bash
   python -m utils.run_dashboard
   ```

3. **Start the data simulator (in a new terminal):**
   ```bash
   python -m utils.simulate_wind_turbine_data
   ```

4. **Access the dashboard:**
   Open your browser and go to `http://localhost:5001`

## System Overview

The anomaly detection system consists of several interconnected components:

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
- **Advanced Stream Processing** with Apache Kafka integration
- **Real-time data streaming** with configurable update frequency
- **Database persistence** with SQLite for reliable data storage
- **Model versioning** with automatic model saving and loading
- **Error handling** with detailed logging and debugging endpoints
- **Backpressure handling** and fault tolerance
- **Time-based and count-based windowing** for batch processing
- **State management** for complex stream operations

## Project Structure

```
anomaly-detection/
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
│   ├── streaming/
│   │   ├── kafka_producer.py        # Advanced Kafka producer with backpressure
│   │   ├── kafka_consumer.py        # Stream processor with windowing
│   │   ├── stream_manager.py        # Stream processing orchestration
│   │   └── __init__.py              # Streaming package initialization
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
│   ├── simulate_wind_turbine_data.py # Data simulation runner
│   └── run_advanced_streaming.py    # Advanced stream processing runner
├── app.log                          # Application logs
├── requirements.txt                 # Python dependencies
└── README.md                        # Project documentation
```

## Data Management

### Utility Commands

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

- **Check sensor data:**
  ```bash
  python utils/check_sensor_data.py
  ```

## Advanced Stream Processing

### Overview
The system now includes advanced stream processing capabilities using Apache Kafka for robust, scalable IoT data processing:

### Features
- **Apache Kafka Integration**: Reliable message queuing and stream processing
- **Advanced Windowing**: Time-based and count-based windowing for batch processing
- **Backpressure Handling**: Automatic flow control to prevent system overload
- **State Management**: Maintains processing state across window operations
- **Real-time Anomaly Detection**: Statistical outlier detection within windows
- **Fault Tolerance**: Error recovery and graceful degradation
- **Comprehensive Monitoring**: Real-time statistics and health monitoring
- **Custom Alert Handlers**: Extensible alert system for anomalies

### Running Advanced Stream Processing

1. **Start Kafka (using Docker):**
   ```bash
   docker run -p 9092:9092 apache/kafka:2.13-3.4.0
   ```

2. **Run the advanced stream processing system:**
   ```bash
   python utils/run_advanced_streaming.py
   ```

3. **Customize stream processing parameters:**
   ```bash
   # Time-based windowing (60-second windows)
   python utils/run_advanced_streaming.py --window-type time --window-size 60
   
   # Count-based windowing (100 messages per window)
   python utils/run_advanced_streaming.py --window-type count --window-size 100
   
   # Custom anomaly probability
   python utils/run_advanced_streaming.py --anomaly-probability 0.1
   
   # Different processing modes
   python utils/run_advanced_streaming.py --mode batch
   ```

### Stream Processing Components

#### Kafka Producer (`kafka_producer.py`)
- **Backpressure Management**: Internal queue with configurable size limits
- **Batch Processing**: Configurable batch sizes and linger times
- **Error Handling**: Automatic retries and error recovery
- **Realistic Data Generation**: Advanced sensor simulation with trends and seasonality

#### Stream Processor (`kafka_consumer.py`)
- **Windowing**: Time-based and count-based window processing
- **Statistical Analysis**: Real-time calculation of window statistics
- **Anomaly Detection**: Statistical outlier detection within windows
- **State Management**: Maintains processing state across operations

#### Stream Manager (`stream_manager.py`)
- **Orchestration**: Coordinates producer, consumer, and simulator
- **Health Monitoring**: Real-time system health checks
- **Alert Management**: Extensible alert handler system
- **Statistics Collection**: Comprehensive performance metrics

### Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--kafka-servers` | Kafka bootstrap servers | `localhost:9092` |
| `--topic` | Kafka topic name | `sensor-data` |
| `--window-type` | Window type (time/count) | `time` |
| `--window-size` | Window size (seconds/count) | `60` |
| `--simulation-interval` | Data generation interval | `1.0s` |
| `--anomaly-probability` | Anomaly injection probability | `0.05` |
| `--mode` | Processing mode | `real_time` |

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

### Stream Processing Dependencies
- **kafka-python 2.0.2** - Apache Kafka client for Python
- **confluent-kafka 1.8.2** - High-performance Kafka client

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

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please:

1. Check the troubleshooting section above
2. Review the logs in `app.log`
3. Open an issue in the repository
4. Contact the development team

## Related Documentation

- [System Architecture](docs/architecture.md)
- [Data Streaming Architecture](docs/streaming_architecture.md)

## Changelog

### Version 1.0.0
- Initial release with anomaly detection system
- Real-time dashboard with sensor monitoring
- API endpoints for data ingestion and retrieval
- Machine learning model with Isolation Forest algorithm
- SQLite database for data persistence

---

**Note**: This system is designed for educational and demonstration purposes. For production use, additional security measures, error handling, and scalability considerations should be implemented.

