"""
Database Model - Handles database operations and data access.
"""

import logging
import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
import os

logger = logging.getLogger(__name__)

class DatabaseModel:
    """Model for handling database operations."""
    
    def __init__(self, db_path: str = "data/wind_turbine.db"):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure the database and tables exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create sensor_readings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT UNIQUE NOT NULL,
                    production_line TEXT NOT NULL,
                    component_id TEXT NOT NULL,
                    temperature REAL NOT NULL,
                    humidity REAL NOT NULL,
                    sound_level REAL NOT NULL,
                    anomaly_score REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON sensor_readings(timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_production_line 
                ON sensor_readings(production_line)
            ''')
            
            conn.commit()
    
    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """Execute a query and return results."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Database query error: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """Execute an update query."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Database update error: {e}")
            return False
    
    def get_table_data(self, table_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get data from a specific table."""
        try:
            with self.get_connection() as conn:
                query = f"SELECT * FROM {table_name} ORDER BY timestamp DESC LIMIT ?"
                df = pd.read_sql_query(query, conn, params=(limit,))
                return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error getting table data: {e}")
            return []
    
    def get_data_samples(self, limit: int = 50) -> Dict[str, Any]:
        """Get sample data for dashboard."""
        try:
            with self.get_connection() as conn:
                # Get recent sensor readings
                sensor_query = '''
                    SELECT timestamp, production_line, component_id, 
                           temperature, humidity, sound_level, anomaly_score
                    FROM sensor_readings 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                '''
                
                sensor_df = pd.read_sql_query(sensor_query, conn, params=(limit,))
                
                # Get summary statistics
                summary_query = '''
                    SELECT 
                        COUNT(*) as total_readings,
                        AVG(temperature) as avg_temperature,
                        AVG(humidity) as avg_humidity,
                        AVG(sound_level) as avg_sound_level,
                        AVG(anomaly_score) as avg_anomaly_score,
                        MIN(timestamp) as earliest_timestamp,
                        MAX(timestamp) as latest_timestamp
                    FROM sensor_readings
                '''
                
                summary_df = pd.read_sql_query(summary_query, conn)
                
                return {
                    'sensor_readings': sensor_df.to_dict('records'),
                    'summary': summary_df.to_dict('records')[0] if not summary_df.empty else {},
                    'total_count': len(sensor_df)
                }
                
        except Exception as e:
            logger.error(f"Error getting data samples: {e}")
            return {'sensor_readings': [], 'summary': {}, 'total_count': 0}
    
    def get_production_line_data(self, production_line: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get data for a specific production line."""
        try:
            with self.get_connection() as conn:
                query = '''
                    SELECT timestamp, component_id, temperature, humidity, sound_level, anomaly_score
                    FROM sensor_readings 
                    WHERE production_line = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                '''
                
                df = pd.read_sql_query(query, conn, params=(production_line, limit))
                return df.to_dict('records')
                
        except Exception as e:
            logger.error(f"Error getting production line data: {e}")
            return []
    
    def get_sensor_correlation(self) -> Dict[str, float]:
        """Get correlation between different sensors."""
        try:
            with self.get_connection() as conn:
                query = '''
                    SELECT temperature, humidity, sound_level
                    FROM sensor_readings 
                    WHERE timestamp >= datetime('now', '-24 hours')
                '''
                
                df = pd.read_sql_query(query, conn)
                
                if len(df) < 2:
                    return {}
                
                correlations = df.corr()
                
                return {
                    'temperature_humidity': float(correlations.loc['temperature', 'humidity']),
                    'temperature_sound': float(correlations.loc['temperature', 'sound_level']),
                    'humidity_sound': float(correlations.loc['humidity', 'sound_level'])
                }
                
        except Exception as e:
            logger.error(f"Error calculating sensor correlation: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 7) -> int:
        """Clean up old data older than specified days."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM sensor_readings 
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_count} old records")
                return deleted_count
                
        except sqlite3.Error as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get total number of records
                cursor.execute("SELECT COUNT(*) FROM sensor_readings")
                total_records = cursor.fetchone()[0]
                
                # Get time range
                cursor.execute("""
                    SELECT 
                        MIN(timestamp) as earliest,
                        MAX(timestamp) as latest,
                        COUNT(DISTINCT production_line) as num_lines,
                        COUNT(DISTINCT component_id) as num_components,
                        AVG(temperature) as avg_temp,
                        AVG(humidity) as avg_humidity,
                        AVG(sound) as avg_sound,
                        AVG(anomaly_score) as avg_anomaly
                    FROM sensor_readings
                """)
                row = cursor.fetchone()
                
                # Get storage size (approximate)
                cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                db_size = cursor.fetchone()[0]
                
                return {
                    'total_records': total_records,
                    'earliest_record': row[0],
                    'latest_record': row[1],
                    'num_production_lines': row[2],
                    'num_components': row[3],
                    'average_temperature': round(row[4], 2) if row[4] else 0,
                    'average_humidity': round(row[5], 2) if row[5] else 0,
                    'average_sound': round(row[6], 2) if row[6] else 0,
                    'average_anomaly_score': round(row[7], 4) if row[7] else 0,
                    'database_size_mb': round(db_size / (1024 * 1024), 2)
                }
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {
                'total_records': 0,
                'earliest_record': None,
                'latest_record': None,
                'num_production_lines': 0,
                'num_components': 0,
                'average_temperature': 0,
                'average_humidity': 0,
                'average_sound': 0,
                'average_anomaly_score': 0,
                'database_size_mb': 0
            }
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database."""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            return False 