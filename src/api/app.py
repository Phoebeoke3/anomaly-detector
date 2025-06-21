from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.train import AnomalyDetector
from data.company_profile import COMPANY_PROFILE

app = Flask(__name__)

# Load the model
try:
    detector = AnomalyDetector.load_model()
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {str(e)}")
    detector = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': detector is not None,
        'company': COMPANY_PROFILE['name'],
        'facility': COMPANY_PROFILE['facility'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/model/status', methods=['GET'])
def model_status():
    """Get model information."""
    if detector is None:
        return jsonify({
            'status': 'error',
            'message': 'Model not loaded'
        }), 500
    
    return jsonify({
        'status': 'loaded',
        'company': COMPANY_PROFILE['name'],
        'model_type': 'IsolationForest',
        'features': ['temperature', 'humidity', 'sound'],
        'production_lines': list(COMPANY_PROFILE['production_lines'].keys()),
        'anomaly_thresholds': COMPANY_PROFILE['anomaly_thresholds'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Predict endpoint for anomaly detection."""
    if detector is None:
        return jsonify({
            'status': 'error',
            'message': 'Model not loaded'
        }), 500
    
    try:
        # Get the request data
        data = request.get_json()
        
        # Convert to DataFrame
        df = pd.DataFrame([data])
        
        # Convert timestamp string to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Make prediction
        scores = detector.predict(df)
        anomaly_score = float(scores[0])
        
        # Get production line configuration
        production_line = data.get('production_line', 'line_1')
        line_config = COMPANY_PROFILE['production_lines'][production_line]['sensor_config']
        
        # Check thresholds and determine status
        status = 'normal'
        if anomaly_score >= COMPANY_PROFILE['anomaly_thresholds']['temperature']['critical']:
            status = 'critical'
        elif anomaly_score >= COMPANY_PROFILE['anomaly_thresholds']['temperature']['warning']:
            status = 'warning'
        
        return jsonify({
            'status': 'success',
            'company': COMPANY_PROFILE['name'],
            'production_line': production_line,
            'component_id': data.get('component_id', 'unknown'),
            'anomaly_score': anomaly_score,
            'status': status,
            'sensor_readings': {
                'temperature': {
                    'value': float(data['temperature']),
                    'normal_range': line_config['temperature']['normal_range'],
                    'warning_range': line_config['temperature']['warning_range']
                },
                'humidity': {
                    'value': float(data['humidity']),
                    'normal_range': line_config['humidity']['normal_range'],
                    'warning_range': line_config['humidity']['warning_range']
                },
                'sound': {
                    'value': float(data['sound']),
                    'normal_range': line_config['sound']['normal_range'],
                    'warning_range': line_config['sound']['warning_range']
                }
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 