"""
API Controller - Handles REST API endpoints and request processing.
"""

import logging
from flask import Flask, request, jsonify
from typing import Dict, Any
from datetime import datetime
import traceback
import os

from src.models.sensor_model import SensorModel
from src.models.anomaly_model import AnomalyModel
from src.models.database_model import DatabaseModel

logger = logging.getLogger(__name__)

class APIController:
    """Controller for handling API requests."""
    
    def __init__(self):
        self.sensor_model = SensorModel()
        self.anomaly_model = AnomalyModel()
        self.database_model = DatabaseModel()
    
    def create_app(self) -> Flask:
        """Create and configure Flask app with API routes."""
        app = Flask(__name__)
        
        # API Routes
        @app.route('/api/predict', methods=['POST'])
        def predict_anomaly():
            print('[DEBUG][API] Using DB path:', os.path.abspath(self.sensor_model.db_path))
            return self._handle_prediction()
        
        @app.route('/api/current-status', methods=['GET'])
        def get_current_status():
            return self._handle_current_status()
        
        @app.route('/api/production-lines', methods=['GET'])
        def get_production_lines():
            return self._handle_production_lines()
        
        @app.route('/api/sensor-history/<sensor_type>', methods=['GET'])
        def get_sensor_history(sensor_type):
            return self._handle_sensor_history(sensor_type)
        
        @app.route('/api/thresholds', methods=['GET'])
        def get_thresholds():
            return self._handle_thresholds()
        
        @app.route('/api/data-samples', methods=['GET'])
        def get_data_samples():
            return self._handle_data_samples()
        
        @app.route('/api/table-data/<table_name>', methods=['GET'])
        def get_table_data(table_name):
            return self._handle_table_data(table_name)
        
        @app.route('/api/debug-sensor-count', methods=['GET'])
        def get_debug_sensor_count():
            return self._handle_debug_sensor_count()
        
        @app.route('/api/health', methods=['GET'])
        def health_check():
            return self._handle_health_check()
        
        return app
    
    def _handle_prediction(self) -> Dict[str, Any]:
        """Handle anomaly prediction requests."""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Validate required fields
            required_fields = ['temperature', 'humidity', 'sound_level']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Add timestamp if not provided
            if 'timestamp' not in data:
                data['timestamp'] = datetime.now().isoformat()
            
            # Map sound_level to sound for database compatibility
            if 'sound_level' in data:
                data['sound'] = data.pop('sound_level')
            
            # Make prediction
            anomaly_score, status = self.anomaly_model.predict(data)
            
            # Store data in database
            if self.sensor_model.insert_sensor_data(data):
                self.sensor_model.update_anomaly_score(data['timestamp'], anomaly_score)
            
            return jsonify({
                'anomaly_score': round(anomaly_score, 4),
                'status': status,
                'timestamp': data['timestamp'],
                'production_line': data.get('production_line', 'turbine-line-1')
            })
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.error(traceback.format_exc())
            return jsonify({'error': 'Internal server error'}), 500
    
    def _handle_current_status(self) -> Dict[str, Any]:
        """Handle current status requests."""
        try:
            # Get model status
            model_status = self.anomaly_model.get_model_status()
            
            # Get recent sensor data
            recent_data = self.sensor_model.get_recent_sensor_data(10)
            
            # Get production line status
            production_status = self.sensor_model.get_production_line_status()
            
            return jsonify({
                'model_status': model_status,
                'recent_data': recent_data,
                'production_lines': production_status,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error getting current status: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def _handle_production_lines(self) -> Dict[str, Any]:
        """Handle production lines status requests."""
        try:
            status = self.sensor_model.get_production_line_status()
            return jsonify(status)
            
        except Exception as e:
            logger.error(f"Error getting production lines: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def _handle_sensor_history(self, sensor_type: str) -> Dict[str, Any]:
        """Handle sensor history requests."""
        try:
            history = self.sensor_model.get_sensor_history(sensor_type, 50)
            return jsonify({
                'sensor_type': sensor_type,
                'data': history,
                'count': len(history)
            })
            
        except Exception as e:
            logger.error(f"Error getting sensor history: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def _handle_thresholds(self) -> Dict[str, Any]:
        """Handle thresholds requests."""
        try:
            thresholds = self.anomaly_model.get_anomaly_thresholds()
            return jsonify(thresholds)
            
        except Exception as e:
            logger.error(f"Error getting thresholds: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def _handle_data_samples(self) -> Dict[str, Any]:
        """Handle data samples requests."""
        try:
            limit = request.args.get('limit', 50, type=int)
            samples = self.database_model.get_data_samples(limit)
            return jsonify(samples)
            
        except Exception as e:
            logger.error(f"Error getting data samples: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def _handle_table_data(self, table_name: str) -> Dict[str, Any]:
        """Handle table data requests."""
        try:
            limit = request.args.get('limit', 100, type=int)
            data = self.database_model.get_table_data(table_name, limit)
            return jsonify({
                'table_name': table_name,
                'data': data,
                'count': len(data)
            })
            
        except Exception as e:
            logger.error(f"Error getting table data: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def _handle_debug_sensor_count(self) -> Dict[str, Any]:
        """Handle debug sensor count requests."""
        try:
            count_info = self.sensor_model.get_sensor_count()
            return jsonify(count_info)
            
        except Exception as e:
            logger.error(f"Error getting sensor count: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def _handle_health_check(self) -> Dict[str, Any]:
        """Handle health check requests."""
        try:
            # Check database connection
            db_stats = self.database_model.get_database_stats()
            
            # Check model status
            model_status = self.anomaly_model.get_model_status()
            
            return jsonify({
                'status': 'healthy',
                'database': 'connected' if db_stats else 'error',
                'model': 'loaded' if model_status.get('model_loaded') else 'error',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500 