from flask import Flask, render_template, jsonify, request
from datetime import datetime
import random
import json
import os
import sys
import pandas as pd
from functools import wraps
import logging
from werkzeug.exceptions import HTTPException

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.train import AnomalyDetector
from data.sqlite_db import SQLiteDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load company configuration
def load_company_config():
    """Load company configuration from file."""
    try:
        with open('config/company_config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading company config: {e}")
        return {}

# Initialize anomaly detector
try:
    detector = AnomalyDetector.load_model()
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    detector = None

# Initialize SQLiteDB
db = SQLiteDB()

def validate_sensor_data(data):
    """Validate sensor data format and ranges for wind turbine component factory."""
    # Required fields
    required_fields = ['temperature', 'humidity', 'sound_level']
    
    # Range validation for wind turbine context
    validations = {
        'temperature': (10, 40),  # °C
        'humidity': (20, 80),    # %
        'sound_level': (40, 90)  # dB
    }
    
    # Check required fields
    if not all(field in data for field in required_fields):
        return False, "Missing required fields"
    
    # Validate ranges
    for field, (min_val, max_val) in validations.items():
        if not (min_val <= data[field] <= max_val):
            return False, f"{field} out of range ({min_val}-{max_val})"
    
    return True, "Valid data"

def handle_errors(f):
    """Error handling decorator."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except HTTPException as e:
            logger.error(f"HTTP error: {e}")
            return jsonify({
                'error': str(e),
                'status_code': e.code
            }), e.code
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e)
            }), 500
    return wrapper

@app.before_request
def log_request_info():
    logging.info(f"Request: {request.method} {request.path} - {request.remote_addr}")

@app.after_request
def log_response_info(response):
    logging.info(f"Response: {response.status} for {request.method} {request.path}")
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Exception: {str(e)}", exc_info=True)
    return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html', company=load_company_config())

@app.route('/data-view')
def data_view():
    """Render the data view page."""
    return render_template('data_view.html', company=load_company_config())

@app.route('/api/current-status')
@handle_errors
def current_status():
    """Get current system status.
    
    Returns:
        JSON object containing:
        - timestamp: Current server time
        - model_status: Model operational status and metrics
        - health_status: System health information
    """
    if detector is None:
        return jsonify({
            'error': 'Model not loaded',
            'status_code': 503
        }), 503
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'model_status': {
            'status': 'operational',
            'version': detector.model_version,
            'metrics': detector.metrics,
            'last_trained': detector.metrics.get('training_date', 'unknown')
        },
        'health_status': {
            'status': 'healthy',
            'message': 'All systems operational'
        }
    })

@app.route('/api/predict', methods=['POST'])
@handle_errors
def predict():
    """Make anomaly predictions for wind turbine component sensor data.
    
    Request body:
        JSON object containing:
        - temperature: float (10-40°C)
        - humidity: float (20-80%)
        - sound_level: float (40-90 dB)
        - production_line: str (optional, defaults to 'turbine-line-1')
        - component_id: str (optional, defaults to 'blade-1')
    
    Returns:
        JSON object containing:
        - anomaly_score: float
        - prediction: str (normal/warning/critical)
        - timestamp: str
        - model_version: str
        - confidence: float
    """
    if detector is None:
        return jsonify({
            'error': 'Model not loaded',
            'status_code': 503
        }), 503
    
    # Get and validate input data
    data = request.get_json()
    if not data:
        return jsonify({
            'error': 'No data provided',
            'status_code': 400
        }), 400
    
    is_valid, message = validate_sensor_data(data)
    if not is_valid:
        return jsonify({
            'error': message,
            'status_code': 400
        }), 400
    
    # Create DataFrame for prediction
    df = pd.DataFrame([{
        'temperature': data['temperature'],
        'humidity': data['humidity'],
        'sound': data['sound_level']  # Map sound_level to sound for model
    }])
    
    # Get prediction
    anomaly_score = float(detector.predict(df)[0])
    
    # Determine status
    status = 'normal'
    if anomaly_score >= detector.metrics['threshold']:
        status = 'critical'
    elif anomaly_score >= detector.metrics['threshold'] * 0.8:
        status = 'warning'
    
    # Store in database with existing schema
    db.insert_sensor_data({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'production_line': data.get('production_line', 'turbine-line-1'),
        'component_id': data.get('component_id', 'blade-1'),
        'temperature': data['temperature'],
        'humidity': data['humidity'],
        'sound': data['sound_level'],  # Map sound_level to sound
        'is_anomaly': 1 if status != 'normal' else 0
    })
    
    return jsonify({
        'anomaly_score': anomaly_score,
        'prediction': status,
        'timestamp': datetime.now().isoformat(),
        'model_version': detector.model_version,
        'confidence': detector.metrics['threshold']
    })

@app.route('/api/production-lines')
@handle_errors
def production_lines():
    """Get status of all production lines.
    
    Returns:
        JSON object containing status and sensor data for each production line.
    """
    if detector is None:
        return jsonify({
            'error': 'Model not loaded',
            'status_code': 503
        }), 503
    
    lines = {}
    for i, line in enumerate(load_company_config().get('production_lines', [])):
        # Generate more varied sensor data to create different statuses
        base_temp = 25 + random.uniform(-3, 3)  # Base temperature with variation
        base_humidity = 50 + random.uniform(-8, 8)  # Base humidity with variation
        base_sound = 60 + random.uniform(-5, 5)  # Base sound with variation
        
        # Add some intentional anomalies for demonstration
        if i == 1:  # Second line - warning conditions
            base_temp += random.uniform(2, 4)  # Higher temperature
            base_humidity += random.uniform(5, 10)  # Higher humidity
        elif i == 2:  # Third line - critical conditions
            base_temp += random.uniform(4, 6)  # Much higher temperature
            base_sound += random.uniform(8, 12)  # Much higher sound
        
        sensor_data = {
            'temperature': round(max(15, min(35, base_temp)), 2),  # Clamp between 15-35°C
            'humidity': round(max(30, min(70, base_humidity)), 2),  # Clamp between 30-70%
            'sound_level': round(max(45, min(75, base_sound)), 2)  # Clamp between 45-75dB
        }
        
        # Create DataFrame for prediction
        df = pd.DataFrame([{
            'temperature': sensor_data['temperature'],
            'humidity': sensor_data['humidity'],
            'sound': sensor_data['sound_level']
        }])
        
        # Get prediction
        anomaly_score = float(detector.predict(df)[0])
        
        # Use more reasonable thresholds for demonstration
        # Get the model's threshold, but use lower values for more variation
        model_threshold = detector.metrics.get('threshold', 0.5)
        warning_threshold = model_threshold * 0.6  # Lower warning threshold
        critical_threshold = model_threshold * 0.8  # Lower critical threshold
        
        # Determine status with more variation
        status = 'normal'
        if anomaly_score >= critical_threshold:
            status = 'critical'
        elif anomaly_score >= warning_threshold:
            status = 'warning'
        
        lines[line['id']] = {
            'name': line['name'],
            'components': line['components'],
            'status': status,
            'anomaly_score': anomaly_score,
            'sensors': sensor_data
        }
    
    return jsonify(lines)

@app.route('/api/thresholds')
@handle_errors
def get_thresholds():
    """Get current anomaly detection thresholds.
    
    Returns:
        JSON object containing current thresholds.
    """
    if detector is None:
        return jsonify({
            'error': 'Model not loaded',
            'status_code': 503
        }), 503
    
    model_threshold = detector.metrics.get('threshold', 0.5)
    warning_threshold = model_threshold * 0.6
    critical_threshold = model_threshold * 0.8
    
    return jsonify({
        'model_threshold': model_threshold,
        'warning_threshold': warning_threshold,
        'critical_threshold': critical_threshold,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/sensor-history/<sensor_type>')
@handle_errors
def sensor_history(sensor_type):
    """Get historical data for a specific sensor type from the database."""
    if sensor_type not in ['temperature', 'humidity', 'sound_level']:
        return jsonify({
            'error': 'Invalid sensor type',
            'status_code': 400
        }), 400
    # Fetch last 24 hours of data
    rows = db.conn.execute(f"""
        SELECT timestamp, {sensor_type} FROM sensor_readings
        WHERE timestamp >= datetime('now', '-24 hours')
        ORDER BY timestamp ASC
    """).fetchall()
    data = []
    for row in rows:
        # Convert timestamp to epoch seconds
        ts = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').timestamp()
        data.append({'timestamp': ts, 'value': row[1]})
    return jsonify(data)

@app.route('/api/debug-sensor-count')
def debug_sensor_count():
    row = db.conn.execute("SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM sensor_readings").fetchone()
    return jsonify({
        'count': row[0],
        'min_timestamp': row[1],
        'max_timestamp': row[2]
    })

@app.route('/api/database-stats')
@handle_errors
def database_stats():
    """Get database statistics.
    
    Returns:
        JSON object containing database statistics.
    """
    try:
        # Get total records
        total_records = db.conn.execute("SELECT COUNT(*) FROM sensor_readings").fetchone()[0]
        
        # Get total tables
        tables = db.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        total_tables = len(tables)
        
        # Get latest record timestamp
        latest_record = db.conn.execute("SELECT MAX(timestamp) FROM sensor_readings").fetchone()[0]
        
        # Get database file size
        db_size = "Unknown"
        try:
            db_path = 'data/wind_turbine.db'
            if os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)
                if size_bytes < 1024:
                    db_size = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    db_size = f"{size_bytes / 1024:.1f} KB"
                else:
                    db_size = f"{size_bytes / (1024 * 1024):.1f} MB"
        except:
            pass
        
        return jsonify({
            'total_records': total_records,
            'total_tables': total_tables,
            'latest_record': latest_record,
            'db_size': db_size,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return jsonify({
            'error': 'Failed to get database statistics',
            'status_code': 500
        }), 500

@app.route('/api/data-samples')
@handle_errors
def data_samples():
    """Get data samples from all tables.
    
    Returns:
        JSON object containing sample data from all tables.
    """
    try:
        # Ensure database connection
        if not db.conn:
            db._connect()
        
        # Get database statistics with error handling
        try:
            total_records = db.conn.execute("SELECT COUNT(*) FROM sensor_readings").fetchone()[0]
        except:
            total_records = 0
            
        try:
            tables = db.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            total_tables = len(tables)
        except:
            tables = []
            total_tables = 0
            
        try:
            latest_record = db.conn.execute("SELECT MAX(timestamp) FROM sensor_readings").fetchone()[0]
        except:
            latest_record = "No data"
        
        # Get database file size
        db_size = "Unknown"
        try:
            db_path = 'data/wind_turbine.db'
            if os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)
                if size_bytes < 1024:
                    db_size = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    db_size = f"{size_bytes / 1024:.1f} KB"
                else:
                    db_size = f"{size_bytes / (1024 * 1024):.1f} MB"
        except:
            pass
        
        database_stats = {
            'total_records': total_records,
            'total_tables': total_tables,
            'latest_record': latest_record,
            'db_size': db_size
        }
        
        # Get sample data from each table
        table_samples = {}
        
        for table in tables:
            table_name = table[0]
            
            try:
                # Get sample data (up to 10 records)
                count = db.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                if count > 0:
                    sample_rows = db.conn.execute(f"SELECT * FROM {table_name} ORDER BY timestamp DESC LIMIT 10").fetchall()
                    columns = [description[0] for description in db.conn.execute(f"SELECT * FROM {table_name} LIMIT 1").description]
                    
                    table_samples[table_name] = []
                    for row in sample_rows:
                        table_samples[table_name].append(dict(zip(columns, row)))
                else:
                    table_samples[table_name] = []
            except Exception as e:
                logger.error(f"Error getting sample data for table {table_name}: {e}")
                table_samples[table_name] = []
        
        return jsonify({
            'database_stats': database_stats,
            'table_samples': table_samples,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting data samples: {e}")
        # Return a minimal response instead of error
        return jsonify({
            'database_stats': {
                'total_records': 0,
                'total_tables': 0,
                'latest_record': 'Error loading data',
                'db_size': 'Unknown'
            },
            'table_samples': {},
            'timestamp': datetime.now().isoformat(),
            'error': 'Some data could not be loaded'
        })

@app.route('/api/table-data/<table_name>')
@handle_errors
def table_data(table_name):
    """Get data from a specific table.
    
    Args:
        table_name: Name of the table to query
        
    Returns:
        JSON object containing table data and metadata.
    """
    try:
        # Ensure database connection
        if not db.conn:
            db._connect()
        
        # Validate table name to prevent SQL injection
        valid_tables = ['sensor_readings', 'model_metadata']
        if table_name not in valid_tables:
            return jsonify({
                'error': 'Invalid table name',
                'status_code': 400
            }), 400
        
        # Get limit parameter
        limit = request.args.get('limit', 50, type=int)
        limit = min(max(limit, 1), 1000)  # Clamp between 1 and 1000
        
        # Get total count with error handling
        try:
            total_count = db.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        except:
            total_count = 0
        
        # Get data from table with error handling
        try:
            rows = db.conn.execute(f"SELECT * FROM {table_name} ORDER BY timestamp DESC LIMIT {limit}").fetchall()
            
            # Get column names
            columns = [description[0] for description in db.conn.execute(f"SELECT * FROM {table_name} LIMIT 1").description]
            
            # Convert rows to dictionaries
            records = []
            for row in rows:
                records.append(dict(zip(columns, row)))
        except Exception as e:
            logger.error(f"Error getting data from table {table_name}: {e}")
            rows = []
            columns = []
            records = []
        
        return jsonify({
            'table_name': table_name,
            'total_count': total_count,
            'returned_count': len(records),
            'limit': limit,
            'records': records,
            'columns': columns,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting table data: {e}")
        # Return a minimal response instead of error
        return jsonify({
            'table_name': table_name,
            'total_count': 0,
            'returned_count': 0,
            'limit': limit,
            'records': [],
            'columns': [],
            'timestamp': datetime.now().isoformat(),
            'error': 'Could not load table data'
        })

@app.route('/api/health')
def health():
    """Health check endpoint for monitoring."""
    try:
        # Check database connection
        db_status = 'ok'
        try:
            db.conn.execute('SELECT 1')
        except Exception:
            db_status = 'error'
        # Check model status
        model_status = 'ok' if detector is not None else 'error'
        return jsonify({
            'status': 'ok' if db_status == 'ok' and model_status == 'ok' else 'error',
            'database': db_status,
            'model': model_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 