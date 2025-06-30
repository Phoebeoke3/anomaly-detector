"""
Dashboard Controller - Handles web interface and template rendering.
"""

import logging
from flask import Flask, render_template, jsonify, request, Response
from typing import Dict, Any
from datetime import datetime
import os
import json
import time
import csv
import sqlite3

from src.models.sensor_model import SensorModel
from src.models.anomaly_model import AnomalyModel
from src.models.database_model import DatabaseModel

logger = logging.getLogger(__name__)

class DashboardController:
    """Controller for handling dashboard requests."""
    
    def __init__(self):
        print('[DEBUG] Initializing SensorModel...')
        self.sensor_model = SensorModel()
        print('[DEBUG] SensorModel initialized.')
        print('[DEBUG] Initializing AnomalyModel...')
        self.anomaly_model = AnomalyModel()
        print('[DEBUG] AnomalyModel initialized.')
        print('[DEBUG] Initializing DatabaseModel...')
        self.database_model = DatabaseModel()
        print('[DEBUG] DatabaseModel initialized.')
        print('[DEBUG] Loading company config...')
        self.company = self._load_company_config()
        print('[DEBUG] Company config loaded.')
        print('[DEBUG] Getting anomaly thresholds...')
        self.thresholds = self.anomaly_model.get_anomaly_thresholds()
        print('[DEBUG] Anomaly thresholds loaded.')
        print('[DEBUG] Getting model status...')
        self.model_status = self.anomaly_model.get_model_status()
        print('[DEBUG] Model status loaded.')
    
    def _load_company_config(self):
        try:
            with open('config/company_config.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading company config: {e}")
            return {"name": "Unknown", "facility": "Unknown"}
    
    def create_app(self) -> Flask:
        """Create and configure Flask app with dashboard routes."""
        # Get the absolute path to the templates directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(current_dir, '..', 'views', 'templates')
        static_dir = os.path.join(current_dir, '..', 'views', 'static')
        
        app = Flask(__name__, 
                   template_folder=template_dir,
                   static_folder=static_dir)
        
        # Dashboard Routes
        @app.route('/')
        def index():
            return self._handle_dashboard()
        
        @app.route('/simple')
        def simple():
            return self._handle_simple_dashboard()
        
        @app.route('/test')
        def test():
            return self._handle_test()
        
        @app.route('/data-view')
        def data_view():
            return self._handle_data_view()
        
        @app.route('/api/dashboard-data')
        def get_dashboard_data():
            return self._handle_dashboard_data()
        
        @app.route('/api/sensor-correlation')
        def get_sensor_correlation():
            return self._handle_sensor_correlation()
        
        @app.route('/api/production-lines')
        def get_production_lines():
            """Get production line data."""
            try:
                data = self.sensor_model.get_production_line_status()
                return jsonify(data)
            except Exception as e:
                logger.error(f"Error getting production line data: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/database-stats')
        def get_database_stats():
            """Get database statistics."""
            try:
                stats = self.database_model.get_database_stats()
                return jsonify(stats)
            except Exception as e:
                logger.error(f"Error getting database stats: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/table-data/<table_name>')
        def get_table_data(table_name):
            """Get data from a specific table."""
            try:
                limit = request.args.get('limit', default=50, type=int)
                
                # Validate table name to prevent SQL injection
                allowed_tables = ['sensor_readings', 'model_metadata']
                if table_name not in allowed_tables:
                    return jsonify({'error': f'Invalid table name. Allowed tables: {", ".join(allowed_tables)}'}), 400
                
                # Get table data
                with self.database_model.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(f'SELECT * FROM {table_name} ORDER BY timestamp DESC LIMIT ?', (limit,))
                    columns = [description[0] for description in cursor.description]
                    rows = cursor.fetchall()
                    
                    # Convert rows to list of dicts
                    records = []
                    for row in rows:
                        record = {}
                        for i, value in enumerate(row):
                            record[columns[i]] = value
                        records.append(record)
                    
                    return jsonify({
                        'table': table_name,
                        'columns': columns,
                        'records': records,
                        'total_records': len(records)
                    })
                    
            except Exception as e:
                logger.error(f"Error getting table data: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/thresholds')
        def get_thresholds():
            return jsonify({
                'warning_threshold': self.thresholds.get('warning_threshold', 0.6),
                'critical_threshold': self.thresholds.get('critical_threshold', 0.8)
            })
        
        @app.route('/api/current-status')
        def get_current_status():
            try:
                production_lines = self.sensor_model.get_production_line_status()
                return jsonify({
                    'status': 'ok',
                    'production_lines': production_lines,
                    'model_status': self.model_status,
                    'health_status': {
                        'status': 'Healthy' if production_lines else 'Warning'
                    },
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500

        @app.route('/api/sensor-history/<sensor_type>')
        def get_sensor_history(sensor_type):
            try:
                # Map frontend sensor types to database column names
                sensor_map = {
                    'temperature': 'temperature',
                    'humidity': 'humidity',
                    'sound_level': 'sound'
                }
                
                # Get the database column name
                db_sensor_type = sensor_map.get(sensor_type)
                if not db_sensor_type:
                    return jsonify({
                        'status': 'error',
                        'message': f'Invalid sensor type: {sensor_type}',
                        'timestamp': datetime.now().isoformat()
                    }), 400

                # Get last 24 hours of data for the sensor type
                history = self.sensor_model.get_sensor_history(db_sensor_type, limit=100)
                return jsonify({
                    'status': 'ok',
                    'sensor_type': sensor_type,
                    'data': history,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error getting sensor history: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @app.route('/api/data-samples')
        def get_data_samples():
            """Get sample data from each table."""
            try:
                samples = {}
                
                # Get sample data from sensor_readings
                with self.database_model.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Get sensor readings samples
                    cursor.execute("""
                        SELECT timestamp, production_line, component_id, 
                               temperature, humidity, sound, anomaly_score, is_anomaly
                        FROM sensor_readings 
                        ORDER BY timestamp DESC 
                        LIMIT 5
                    """)
                    columns = [description[0] for description in cursor.description]
                    rows = cursor.fetchall()
                    
                    sensor_samples = []
                    for row in rows:
                        sample = {}
                        for i, value in enumerate(row):
                            # Format timestamp for readability
                            if columns[i] == 'timestamp':
                                sample[columns[i]] = value
                            # Format boolean for readability
                            elif columns[i] == 'is_anomaly':
                                sample[columns[i]] = 'Yes' if value else 'No'
                            # Round float values
                            elif isinstance(value, float):
                                sample[columns[i]] = round(value, 3)
                            else:
                                sample[columns[i]] = value
                        sensor_samples.append(sample)
                    
                    # Try to get model metadata samples (handle case where table might not exist)
                    try:
                        cursor.execute("PRAGMA table_info(model_metadata)")
                        table_info = cursor.fetchall()
                        
                        if table_info:
                            # Get column names from the table
                            columns = [col[1] for col in table_info]
                            
                            # Build query dynamically based on available columns
                            select_columns = ', '.join(columns)
                            cursor.execute(f"""
                                SELECT {select_columns}
                                FROM model_metadata 
                                ORDER BY timestamp DESC 
                                LIMIT 5
                            """)
                            
                            rows = cursor.fetchall()
                            model_samples = []
                            for row in rows:
                                sample = {}
                                for i, value in enumerate(row):
                                    if isinstance(value, float):
                                        sample[columns[i]] = round(value, 3)
                                    else:
                                        sample[columns[i]] = value
                                model_samples.append(sample)
                        else:
                            model_samples = []
                            
                    except Exception as e:
                        logger.warning(f"Could not fetch model metadata: {e}")
                        model_samples = []
                    
                    return jsonify({
                        'samples': {
                            'sensor_readings': sensor_samples,
                            'model_metadata': model_samples
                        }
                    })
                    
            except Exception as e:
                logger.error(f"Error getting data samples: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/predictions')
        def predictions():
            return render_template('predictions.html', company=self.company, model_status=self.model_status, thresholds=self.thresholds, timestamp=datetime.now().isoformat())
        
        @app.route('/export-csv')
        def export_csv():
            import os
            print('[DEBUG] Exporting from DB path:', os.path.abspath(self.sensor_model.db_path))
            def generate():
                with sqlite3.connect(self.sensor_model.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 1000')
                    rows = cursor.fetchall()
                    if not rows:
                        yield 'No data to export\n'
                        return
                    header = [description[0] for description in cursor.description]
                    yield ','.join(header) + '\n'
                    for row in rows:
                        row = list(row)
                        # Format timestamp if present
                        if 'timestamp' in header:
                            idx = header.index('timestamp')
                            try:
                                # Try to parse and reformat if not already string
                                import datetime
                                if not isinstance(row[idx], str):
                                    row[idx] = str(row[idx])
                                else:
                                    # Try to parse and format
                                    try:
                                        dt = datetime.datetime.fromisoformat(row[idx])
                                        row[idx] = dt.strftime('%Y-%m-%d %H:%M:%S')
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                        yield ','.join(map(str, row)) + '\n'
            return Response(generate(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=sensor_readings.csv'})

        @app.route('/export-predictions-csv')
        def export_predictions_csv():
            def generate():
                with sqlite3.connect(self.sensor_model.db_path) as conn:
                    cursor = conn.cursor()
                    # Try to select relevant columns for predictions
                    try:
                        cursor.execute('''
                            SELECT timestamp, production_line, component_id, anomaly_score, is_anomaly
                            FROM sensor_readings
                            ORDER BY timestamp DESC
                            LIMIT 1000
                        ''')
                        rows = cursor.fetchall()
                        if not rows:
                            yield 'No predictions to export\n'
                            return
                        header = [description[0] for description in cursor.description]
                        yield ','.join(header) + '\n'
                        for row in rows:
                            row = list(row)
                            # Format timestamp
                            if 'timestamp' in header:
                                idx = header.index('timestamp')
                                try:
                                    import datetime
                                    if not isinstance(row[idx], str):
                                        row[idx] = str(row[idx])
                                    else:
                                        try:
                                            dt = datetime.datetime.fromisoformat(row[idx])
                                            row[idx] = dt.strftime('%Y-%m-%d %H:%M:%S')
                                        except Exception:
                                            pass
                                except Exception:
                                    pass
                            yield ','.join(map(str, row)) + '\n'
                    except Exception as e:
                        yield f'Error exporting predictions: {e}\n'
            return Response(generate(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=predictions.csv'})
        
        # Minimal health check route
        @app.route('/ping')
        def ping():
            return "OK"
        
        return app
    
    def _handle_dashboard(self) -> str:
        """Handle main dashboard page."""
        try:
            start_time = time.time()
            # Use cached company config, model status, and thresholds
            company = self.company
            model_status = self.model_status
            thresholds = self.thresholds
            # Only fetch production status (DB) on each request
            t0 = time.time()
            production_status = self.sensor_model.get_production_line_status()
            t1 = time.time()
            print(f"[TIMER] Get production line status: {t1-t0:.3f}s")

            context = {
                'company': company,
                'model_status': model_status,
                'production_lines': production_status,
                'thresholds': thresholds,
                'timestamp': datetime.now().isoformat()
            }

            t0 = time.time()
            result = render_template('index.html', **context)
            t1 = time.time()
            print(f"[TIMER] Render template: {t1-t0:.3f}s")

            total_time = time.time() - start_time
            print(f"[TIMER] Total dashboard load time: {total_time:.3f}s")
            return result

        except Exception as e:
            logger.error(f"Error rendering dashboard: {e}")
            return render_template('error.html', error=str(e))
    
    def _handle_simple_dashboard(self) -> str:
        """Handle simple dashboard page without database operations."""
        try:
            start_time = time.time()
            print(f"[TIMER] Starting simple dashboard")
            
            # Load company config only
            t0 = time.time()
            with open('config/company_config.json', 'r') as f:
                company = json.load(f)
            t1 = time.time()
            print(f"[TIMER] Load company config: {t1-t0:.3f}s")

            # Skip all database operations
            context = {
                'company': company,
                'model_status': {'model_loaded': True, 'model_type': 'IsolationForest'},
                'production_lines': {},
                'thresholds': {'normal_threshold': 0.3, 'warning_threshold': 0.6, 'anomaly_threshold': 0.8},
                'timestamp': datetime.now().isoformat()
            }

            t0 = time.time()
            result = render_template('index.html', **context)
            t1 = time.time()
            print(f"[TIMER] Render template: {t1-t0:.3f}s")

            total_time = time.time() - start_time
            print(f"[TIMER] Total simple dashboard load time: {total_time:.3f}s")
            return result

        except Exception as e:
            logger.error(f"Error rendering simple dashboard: {e}")
            return render_template('error.html', error=str(e))
    
    def _handle_test(self) -> str:
        """Handle test page."""
        try:
            context = {
                'company': {'name': 'Test Company'},
                'timestamp': datetime.now().isoformat()
            }
            return render_template('test.html', **context)
        except Exception as e:
            logger.error(f"Error rendering test page: {e}")
            return f"Error: {str(e)}"
    
    def _handle_data_view(self) -> str:
        """Handle data view page."""
        try:
            # Get database statistics
            db_stats = self.database_model.get_database_stats()
            
            context = {
                'company': self.company,
                'db_stats': db_stats,
                'timestamp': datetime.now().isoformat()
            }
            
            return render_template('data_view.html', **context)
            
        except Exception as e:
            logger.error(f"Error rendering data view: {e}")
            return render_template('error.html', error=str(e))
    
    def _handle_dashboard_data(self) -> Dict[str, Any]:
        """Handle dashboard data API requests."""
        try:
            # Get recent sensor data
            recent_data = self.sensor_model.get_recent_sensor_data(50)
            
            # Get production line status
            production_status = self.sensor_model.get_production_line_status()
            
            # Get sensor history for charts
            temp_history = self.sensor_model.get_sensor_history('temperature', 30)
            humidity_history = self.sensor_model.get_sensor_history('humidity', 30)
            sound_history = self.sensor_model.get_sensor_history('sound_level', 30)
            
            # Get anomaly score distribution
            anomaly_scores = [item.get('anomaly_score', 0) for item in recent_data if item.get('anomaly_score') is not None]
            
            return jsonify({
                'recent_data': recent_data,
                'production_lines': production_status,
                'sensor_history': {
                    'temperature': temp_history,
                    'humidity': humidity_history,
                    'sound_level': sound_history
                },
                'anomaly_distribution': {
                    'scores': anomaly_scores,
                    'normal_count': len([s for s in anomaly_scores if s < 0.3]),
                    'warning_count': len([s for s in anomaly_scores if 0.3 <= s < 0.6]),
                    'anomaly_count': len([s for s in anomaly_scores if s >= 0.6])
                },
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def _handle_sensor_correlation(self) -> Dict[str, Any]:
        """Handle sensor correlation API requests."""
        try:
            # Get recent sensor data for correlation analysis
            recent_data = self.sensor_model.get_recent_sensor_data(100)
            
            # Extract sensor values
            temperatures = [d['temperature'] for d in recent_data]
            humidities = [d['humidity'] for d in recent_data]
            sound_levels = [d['sound'] for d in recent_data]
            
            return jsonify({
                'temperatures': temperatures,
                'humidities': humidities,
                'sound_levels': sound_levels,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error getting sensor correlation: {e}")
            return jsonify({'error': str(e)}), 500
            
    def _handle_production_lines(self) -> Dict[str, Any]:
        """Handle production lines API requests."""
        try:
            # Get production line status from SensorModel
            production_status = self.sensor_model.get_production_line_status()
            return jsonify(production_status)
            
        except Exception as e:
            logger.error(f"Error getting production lines: {e}")
            return jsonify({'error': str(e)}), 500 