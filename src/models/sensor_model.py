"""
Sensor Model - Handles sensor data operations and validation.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import sqlite3
import os
import time
import json

logger = logging.getLogger(__name__)

class SensorModel:
    """Model for handling sensor data operations."""
    
    def __init__(self, db_path: str = "data/wind_turbine.db"):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure the database and tables exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create sensor_readings table with schema matching SQLiteDB
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    timestamp DATETIME,
                    production_line TEXT,
                    component_id TEXT,
                    temperature REAL,
                    humidity REAL,
                    sound REAL,
                    is_anomaly INTEGER,
                    anomaly_score REAL,
                    PRIMARY KEY (production_line, timestamp, component_id)
                )
            ''')
            
            conn.commit()
    
    def validate_sensor_data(self, data: Dict[str, Any]) -> bool:
        """Validate incoming sensor data."""
        required_fields = ['temperature', 'humidity', 'sound', 'timestamp']
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate data types and ranges
        try:
            temperature = float(data['temperature'])
            humidity = float(data['humidity'])
            sound = float(data['sound'])
            
            # Validate ranges for wind turbine manufacturing
            if not (10 <= temperature <= 40):
                logger.warning(f"Temperature out of range: {temperature}")
            
            if not (20 <= humidity <= 80):
                logger.warning(f"Humidity out of range: {humidity}")
            
            if not (40 <= sound <= 90):
                logger.warning(f"Sound level out of range: {sound}")
                
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid data type: {e}")
            return False
        
        return True
    
    def insert_sensor_data(self, data: Dict[str, Any]) -> bool:
        """Insert sensor data into database."""
        if not self.validate_sensor_data(data):
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Use INSERT OR REPLACE to handle duplicates
                cursor.execute('''
                    INSERT OR REPLACE INTO sensor_readings 
                    (timestamp, production_line, component_id, temperature, humidity, sound)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    data['timestamp'],
                    data.get('production_line', 'turbine-line-1'),
                    data.get('component_id', 'blade-1'),
                    data['temperature'],
                    data['humidity'],
                    data['sound']
                ))
                
                conn.commit()
                logger.info(f"Inserted data for {data.get('production_line', 'turbine-line-1')} - {data.get('component_id', 'blade-1')}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error inserting sensor data: {e}")
            return False
    
    def update_anomaly_score(self, timestamp: str, anomaly_score: float) -> bool:
        """Update anomaly score for a specific timestamp."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sensor_readings 
                    SET anomaly_score = ? 
                    WHERE timestamp = ?
                ''', (anomaly_score, timestamp))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error updating anomaly score: {e}")
            return False
    
    def get_recent_sensor_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent sensor data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT timestamp, production_line, component_id, temperature, humidity, sound, is_anomaly, anomaly_score
                    FROM sensor_readings 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                return [
                    {
                        'timestamp': row[0],
                        'production_line': row[1],
                        'component_id': row[2],
                        'temperature': row[3],
                        'humidity': row[4],
                        'sound': row[5],
                        'is_anomaly': row[6],
                        'anomaly_score': row[7]
                    }
                    for row in rows
                ]
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching sensor data: {e}")
            return []
    
    def get_sensor_history(self, sensor_type: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get historical data for a specific sensor type."""
        if sensor_type not in ['temperature', 'humidity', 'sound']:
            return []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    SELECT timestamp, {sensor_type}, is_anomaly, production_line
                    FROM sensor_readings 
                    ORDER BY timestamp ASC 
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                return [
                    {
                        'timestamp': row[0],
                        'value': float(row[1]) if row[1] is not None else 0.0,
                        'is_anomaly': bool(row[2]) if row[2] is not None else False,
                        'production_line': row[3]
                    }
                    for row in rows
                ]
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching {sensor_type} history: {e}")
            return []
    
    def get_production_line_status(self) -> Dict[str, Any]:
        """Get current status of production lines for dashboard."""
        try:
            with open('config/company_config.json', 'r') as f:
                company = json.load(f)
            lines = company.get('production_lines', [])

            # Initialize anomaly model
            from src.models.anomaly_model import AnomalyModel
            anomaly_model = AnomalyModel()

            # Get recent sensor data for each line
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                status = {}
                for line in lines:
                    line_id = line['id']
                    cursor.execute('''
                        SELECT AVG(temperature), AVG(humidity), AVG(sound)
                        FROM sensor_readings
                        WHERE production_line = ? AND timestamp >= datetime('now', '-1 hour')
                    ''', (line_id,))
                    row = cursor.fetchone()
                    avg_temp = row[0] if row[0] else 0
                    avg_humidity = row[1] if row[1] else 0
                    avg_sound = row[2] if row[2] else 0

                    # Use anomaly model to predict status
                    sensor_data = {
                        'temperature': avg_temp,
                        'humidity': avg_humidity,
                        'sound_level': avg_sound
                    }
                    anomaly_score, status_str = anomaly_model.predict(sensor_data)

                    status[line_id] = {
                        'name': line['name'],
                        'components': line['components'],
                        'status': status_str,
                        'anomaly_score': anomaly_score,
                        'sensors': {
                            'temperature': avg_temp,
                            'humidity': avg_humidity,
                            'sound_level': avg_sound
                        }
                    }
                return status
        except Exception as e:
            logger.error(f"Error fetching production line status: {e}")
            return {}
    
    def get_sensor_count(self) -> Dict[str, Any]:
        """Get sensor data count and timestamp range."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) as total_count,
                           MIN(timestamp) as earliest,
                           MAX(timestamp) as latest
                    FROM sensor_readings
                ''')
                
                row = cursor.fetchone()
                return {
                    'total_count': row[0],
                    'earliest_timestamp': row[1],
                    'latest_timestamp': row[2]
                }
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching sensor count: {e}")
            return {'total_count': 0, 'earliest_timestamp': None, 'latest_timestamp': None} 