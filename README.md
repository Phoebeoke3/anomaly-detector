# Anomaly Detection System for Wind Turbine Component Manufacturing

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0.1-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive real-time anomaly detection system for wind turbine component manufacturing facilities, featuring advanced sensor data monitoring, machine learning-based anomaly detection, stream processing capabilities, and an interactive dashboard for factory managers and shop floor employees.

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
  - [Stream Processing Features](#stream-processing-features)
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
  - [Stream Processing Endpoints](#stream-processing-endpoints)
- [Data Source and Simulation](#data-source-and-simulation)
  - [Data Generation Parameters](#data-generation-parameters)
  - [Data Stream Features](#data-stream-features)
- [Dependencies](#dependencies)
  - [Core Dependencies](#core-dependencies)
  - [Stream Processing Dependencies](#stream-processing-dependencies)
  - [Frontend Dependencies](#frontend-dependencies)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Debug Steps](#debug-steps)
- [Monitoring & Logging](#monitoring--logging)
- [Support](#support)

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

#### Option 1: Complete System with Stream Processing (Recommended)

1. **Start the API server (port 5000):**
   ```bash
   python -m utils.run_api
   ```

2. **Start the dashboard server (port 5001) in a new terminal:**
   ```bash
   python -m utils.run_dashboard
   ```

3. **Start stream processing with dashboard integration (in a new terminal):**
   ```bash
   python -m utils.run_streaming_with_dashboard --window-size 30 --anomaly-probability 0.1
   ```

4. **Access the dashboard:**
   Open your browser and go to `http://localhost:5001`

#### Option 2: Simple Stream Processing Only

For testing stream processing without the web dashboard:

```bash
python utils/run_simple_streaming.py --window-size 30 --anomaly-probability 0.1
```

#### Option 3: Direct Server Start

Alternatively, you can start the servers directly:

```bash
# Start API server
python src/api/main.py

# Start dashboard server (in new terminal)
python src/dashboard/main.py

# Start stream processing (in new terminal)
python -m utils.run_streaming_with_dashboard --window-size 30 --anomaly-probability 0.1
```

## System Overview

The anomaly detection system consists of several interconnected components designed for production-ready wind turbine manufacturing:

- **Sensor Data**: Realistic wind turbine sensor data simulation (temperature, humidity, sound levels)
- **Data Ingestion**: Continuous data streaming with configurable intervals
- **Data Storage**: SQLite database for persistence and historical analysis
- **Anomaly Detection API**: Flask-based REST API with real-time ML predictions
- **Advanced Stream Processing**: Real-time data processing with windowing and statistical analysis
- **Dashboard**: Interactive web interface for monitoring production lines and sensor data
- **Monitoring & Logging**: Comprehensive logging of all API requests, predictions, and system health

### Current System Status

 **API Server**: Running on port 5000 with real-time anomaly detection  
 **Dashboard Server**: Running on port 5001 with live data visualization  
 **Stream Processing**: Advanced IoT data processing with windowing and statistical analysis  
 **Database**: SQLite storage with real-time data persistence  
 **Real-time Monitoring**: Live dashboard with stream processing statistics  

**Access your dashboard at: `http://localhost:5001`**

## Features

### Core Functionality
- **Real-time monitoring** of wind turbine component manufacturing processes
- **Machine learning-based anomaly detection** using Isolation Forest algorithm
- **Interactive dashboard** with live sensor data visualization
- **Multiple production line monitoring** (Blade Production, Nacelle Assembly)
- **Configurable sensor thresholds** for different manufacturing conditions
- **Historical data tracking** with 24-hour data retention
- **System health monitoring** with health check endpoints
- **Production-ready architecture** with error handling and scalability

### Dashboard Features
- **System Status**: Real-time status of anomaly detection model and system health
- **Production Lines**: Live monitoring of wind turbine production lines with status indicators
- **Sensor Data**: Real-time visualization of temperature, humidity, and sound level data
- **Anomaly Analysis**: Live anomaly score distribution and historical trends
- **System Statistics**: Total production lines, normal/warning/critical status counts, and average anomaly scores
- **Stream Processing Statistics**: Real-time metrics from stream processing system
- **Data Export**: CSV export functionality for data analysis
- **Responsive Design**: Works on desktop and mobile devices

### Technical Features
- **RESTful API** with comprehensive endpoints
- **Advanced Stream Processing** with Apache Kafka integration (with mock fallback)
- **Real-time data streaming** with configurable update frequency
- **Database persistence** with SQLite for reliable data storage
- **Model versioning** with automatic model saving and loading
- **Error handling** with detailed logging and debugging endpoints
- **Backpressure handling** and fault tolerance
- **Time-based and count-based windowing** for batch processing
- **State management** for complex stream operations
- **Live Dashboard** with real-time data visualization
- **Multi-production line monitoring** (blade production, nacelle assembly)

### Stream Processing Features
- **Real-time windowing**: Time-based and count-based batch processing
- **Statistical anomaly detection**: Multiple anomaly types (outliers, spikes, drift, noise)
- **State management**: Processing state across window operations
- **Backpressure handling**: Automatic flow control to prevent system overload
- **Real-time monitoring**: Live statistics and health monitoring
- **Dashboard integration**: Stream processing results displayed in real-time dashboard
- **Configurable parameters**: Window sizes, anomaly probabilities, processing intervals

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
│   │   ├── dashboard_integration.py # Stream processing dashboard integration
│   │   ├── kafka_producer.py        # Advanced Kafka producer with backpressure
│   │   ├── kafka_consumer.py        # Stream processor with windowing
│   │   ├── mock_kafka.py            # Mock Kafka implementation for development
│   │   ├── stream_manager.py        # Stream processing orchestration
│   │   └── __init__.py              # Streaming package initialization
│   └── views/
│       ├── static/                  # CSS, JS, and static assets
│       └── templates/
│           ├── data_view.html       # Data visualization page
│           ├── index.html           # Main dashboard
│           └── predictions.html     # Predictions page
├── utils/
│   ├── check_db.py                  # Database checking utility
│   ├── check_sensor_data.py         # Sensor data validation
│   ├── run_api.py                   # API server runner
│   ├── run_dashboard.py             # Dashboard server runner
│   ├── run_advanced_streaming.py    # Advanced stream processing runner
│   ├── run_simple_streaming.py      # Simple stream processing runner
│   ├── run_streaming_with_dashboard.py # Stream processing with dashboard integration
│   ├── setup_kaggle.py              # Kaggle dataset setup
│   └── simulate_wind_turbine_data.py # Data simulation runner
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
The system includes advanced stream processing capabilities designed for production IoT environments:

### Features
- **Apache Kafka Integration**: Reliable message queuing and stream processing (with mock fallback)
- **Advanced Windowing**: Time-based and count-based windowing for batch processing
- **Backpressure Handling**: Automatic flow control to prevent system overload
- **State Management**: Maintains processing state across window operations
- **Real-time Anomaly Detection**: Statistical outlier detection within windows
- **Fault Tolerance**: Error recovery and graceful degradation
- **Comprehensive Monitoring**: Real-time statistics and health monitoring
- **Dashboard Integration**: Stream processing results displayed in real-time dashboard
- **Multiple Anomaly Types**: Statistical outliers, spikes, drift, and noise detection

### Running Advanced Stream Processing

#### Option 1: Stream Processing with Dashboard Integration (Recommended)

For complete system with real-time dashboard integration:

```bash
python -m utils.run_streaming_with_dashboard --window-size 30 --anomaly-probability 0.1
```

**Features:**
- Real-time stream processing with dashboard integration
- Live statistics displayed in dashboard
- Configurable window sizes and anomaly probabilities
- Multiple production line monitoring
- Real-time anomaly alerts

#### Option 2: Simple Stream Processing (No Dashboard)

For development and testing without web dashboard:

```bash
python utils/run_simple_streaming.py --window-size 30 --anomaly-probability 0.1
```

**Features:**
- In-memory stream processing with threading
- Realistic sensor data simulation with trends and seasonality
- Time-based and count-based windowing
- Statistical anomaly detection
- Real-time monitoring and statistics
- No external dependencies

#### Option 3: Full Kafka Stream Processing

For production-like environments with Apache Kafka:

1. **Start Kafka (using Docker):**
   ```bash
   docker run -p 9092:9092 apache/kafka:2.13-3.4.0
   ```

2. **Run the advanced stream processing system:**
   ```bash
   python utils/run_advanced_streaming.py
   ```

### Stream Processing Configuration

**Time-based windowing (30-second windows):**
```bash
python -m utils.run_streaming_with_dashboard --window-type time --window-size 30
```

**Count-based windowing (50 messages per window):**
```bash
python -m utils.run_streaming_with_dashboard --window-type count --window-size 50
```

**Faster data generation (0.5 second intervals):**
```bash
python -m utils.run_streaming_with_dashboard --simulation-interval 0.5
```

**Higher anomaly probability (10%):**
```bash
python -m utils.run_streaming_with_dashboard --anomaly-probability 0.1
```

### Stream Processing Components

#### Stream Manager (`stream_manager.py`)
- **Orchestration**: Coordinates producer, consumer, and simulator
- **Health Monitoring**: Real-time system health checks
- **Alert Management**: Extensible alert handler system
- **Statistics Collection**: Comprehensive performance metrics
- **Dashboard Integration**: Real-time statistics reporting

#### Stream Processor (`kafka_consumer.py`)
- **Windowing**: Time-based and count-based window processing
- **Statistical Analysis**: Real-time calculation of window statistics
- **Anomaly Detection**: Statistical outlier detection within windows
- **State Management**: Maintains processing state across operations
- **Multiple Anomaly Types**: Outliers, spikes, drift, and noise detection

#### Dashboard Integration (`dashboard_integration.py`)
- **Real-time Statistics**: Stream processing metrics sent to dashboard
- **Database Storage**: Stream processing results stored for historical analysis
- **API Endpoints**: Stream processing statistics available via REST API
- **Live Updates**: Real-time dashboard updates with stream processing data

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

### Stream Processing Endpoints
- `GET /api/stream-processing-stats` - Get real-time stream processing statistics
- `GET /api/stream-anomalies` - Get recent stream processing anomalies
- `GET /api/stream-windows` - Get recent stream processing windows

## Data Source and Simulation

The system uses simulated sensor data that mimics real wind turbine component manufacturing conditions:

### Data Generation Parameters
- **Temperature**: 10-40°C (normal range for blade production)
- **Humidity**: 20-80% (normal range for resin curing)
- **Sound Level**: 40-90 dB (normal range for assembly operations)

### Data Stream Features
- Continuous data generation with configurable intervals (1-second default)
- Realistic noise and patterns with trends and seasonality
- Anomaly injection for testing and validation
- Multiple production line simulation (blade production, nacelle assembly)
- Real-time data streaming with backpressure handling

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
   - Try accessing `http://127.0.0.1:5001` instead of `localhost:5001`

2. **No data appearing in dashboard:**
   - Make sure the stream processing system is running
   - Check database connection and data insertion
   - Verify API endpoints are responding correctly
   - Check that the API server is receiving POST requests to `/api/predict`

3. **Stream processing statistics showing zeros:**
   - Ensure stream processing with dashboard integration is running
   - Check that the correct script is being used: `python -m utils.run_streaming_with_dashboard`
   - Verify database tables are created correctly
   - Check for import errors in stream processing modules

4. **404 errors from simulator:**
   - Check which port your API server is running on
   - Update the simulator's `API_URL` in `utils/simulate_wind_turbine_data.py`
   - Ensure `/api/predict` endpoint is available

5. **System status stuck loading:**
   - Check API response format
   - Verify all required fields are present in API responses
   - Check browser network tab for failed requests

6. **Connection refused errors:**
   - Ensure servers are started in the correct order (API first, then dashboard)
   - Check that ports 5000 and 5001 are not being used by other applications
   - Verify firewall settings are not blocking the connections

### Debug Steps

1. **Check server logs:**
   - Monitor `app.log` for backend errors
   - Check terminal output for server errors
   - Look for successful API requests in the logs

2. **Verify API endpoints:**
   - Test `/api/health` endpoint: `http://localhost:5000/api/health`
   - Check `/api/current-status` response format
   - Verify `/api/predict` is receiving POST requests
   - Test stream processing stats: `http://localhost:5001/api/stream-processing-stats`

3. **Database issues:**
   - Run `python utils/check_db.py` to verify database connection
   - Check if data is being inserted correctly
   - Verify SQLite database file exists in `data/wind_turbine.db`

4. **Model issues:**
   - Verify model files exist in `models/` directory
   - Check model loading in anomaly detection code
   - Look for sklearn warnings about feature names (these are normal)

5. **Stream processing issues:**
   - Check that stream processing is running with dashboard integration
   - Verify database tables for stream processing exist
   - Check for import errors in stream processing modules
   - Ensure the correct Python module path is used (`python -m utils.run_streaming_with_dashboard`)

6. **Network connectivity:**
   - Use `netstat -an | findstr :500` to check if servers are listening
   - Test with `curl http://localhost:5000/api/health` or browser
   - Check if antivirus/firewall is blocking connections

## Monitoring & Logging

- **Application logs**: All API requests, responses, and errors are logged to `app.log`
- **System health**: Check system health at `/api/health` endpoint
- **Database monitoring**: Use debug endpoints to monitor data flow
- **Performance monitoring**: Track API response times and system performance
- **Real-time dashboard**: Live monitoring at `http://localhost:5001`
- **Stream processing stats**: Real-time statistics from stream processing systems
- **API request monitoring**: Live tracking of POST requests to `/api/predict`
- **Stream processing monitoring**: Real-time metrics and anomaly detection rates


## Support

For support, please:

1. Check the troubleshooting section above
2. Review the logs in `app.log`
3. Open an issue in the repository
4. Contact the development team



