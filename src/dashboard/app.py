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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
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

@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html', company=load_company_config())

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
        'sound': data['sound_level']
    }])
    
    # Get prediction
    anomaly_score = float(detector.predict(df)[0])
    
    # Determine status
    status = 'normal'
    if anomaly_score >= detector.metrics['threshold']:
        status = 'critical'
    elif anomaly_score >= detector.metrics['threshold'] * 0.8:
        status = 'warning'
    
    # Store in database
    db.insert_sensor_data({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sensor_id': data.get('sensor_id', 'simulator-1'),
        'temperature': data['temperature'],
        'humidity': data['humidity'],
        'sound_level': data['sound_level'],
        'anomaly_score': anomaly_score,
        'prediction': status
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

if __name__ == '__main__':
    app.run(debug=True, port=5000) 