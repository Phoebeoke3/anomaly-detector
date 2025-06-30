import os
import sys
import sqlite3
from datetime import datetime
import pandas as pd
import logging
import json
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLiteDB:
    """SQLite database handler for sensor data."""
    
    def __init__(self):
        """Initialize SQLite connection."""
        load_dotenv()
        
        # Get database path from environment variables or use default
        self.db_path = os.getenv('SQLITE_DB_PATH', 'data/wind_turbine.db')
        
        self.conn = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish connection to SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            logger.info(f"Connected to SQLite database: {self.db_path}")
        except Exception as e:
            logger.error(f"Error connecting to SQLite: {e}")
            raise
    
    def _create_tables(self):
        """Create required tables if they don't exist."""
        try:
            cursor = self.conn.cursor()
            
            # Create sensor readings table with correct schema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    timestamp DATETIME,
                    production_line TEXT,
                    component_id TEXT,
                    temperature REAL,
                    humidity REAL,
                    sound_level REAL,
                    is_anomaly INTEGER,
                    anomaly_score REAL,
                    PRIMARY KEY (production_line, timestamp, component_id)
                )
            """)
            
            # Create model metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_metadata (
                    model_version TEXT PRIMARY KEY,
                    training_date DATETIME,
                    metrics TEXT
                )
            """)
            
            self.conn.commit()
            logger.info("Created required tables")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def insert_sensor_data(self, data):
        """Insert sensor data into SQLite."""
        try:
            # Ensure we have a valid connection
            if not self.conn:
                self._connect()
            
            query = """
                INSERT OR REPLACE INTO sensor_readings (
                    timestamp, production_line, component_id, temperature, humidity,
                    sound_level, is_anomaly, anomaly_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor = self.conn.cursor()
            cursor.execute(query, (
                data['timestamp'],
                data['production_line'],
                data['component_id'],
                data['temperature'],
                data['humidity'],
                data['sound_level'],
                data['is_anomaly'],
                data['anomaly_score']
            ))
            
            # Commit the transaction
            self.conn.commit()
            logger.info(f"Inserted data for {data['production_line']} - {data['component_id']}")
        except Exception as e:
            logger.error(f"Error inserting sensor data: {e}")
            # Try to rollback if there's an active transaction
            try:
                if self.conn:
                    self.conn.rollback()
            except:
                pass
            # Try to reconnect if connection is lost
            try:
                self._connect()
            except:
                pass
            raise
    
    def get_sensor_history(self, production_line, hours=24):
        """Get historical data for a specific production line."""
        try:
            query = """
                SELECT timestamp, temperature, humidity, sound_level,
                       is_anomaly
                FROM sensor_readings
                WHERE production_line = ?
                AND timestamp > datetime('now', ?)
                ORDER BY timestamp DESC
            """
            
            start_time = f'-{hours} hours'
            df = pd.read_sql_query(query, self.conn, params=(production_line, start_time))
            return df
        except Exception as e:
            logger.error(f"Error retrieving sensor history: {e}")
            raise
    
    def save_model_metadata(self, model_version, metrics):
        """Save model metadata to SQLite."""
        try:
            query = """
                INSERT INTO model_metadata (
                    model_version, training_date, metrics
                ) VALUES (?, ?, ?)
            """
            
            cursor = self.conn.cursor()
            cursor.execute(query, (
                model_version,
                datetime.now(),
                json.dumps(metrics)
            ))
            self.conn.commit()
            logger.info(f"Saved metadata for model version {model_version}")
        except Exception as e:
            logger.error(f"Error saving model metadata: {e}")
            raise
    
    def get_model_metadata(self, model_version):
        """Get model metadata from SQLite."""
        try:
            query = """
                SELECT metrics
                FROM model_metadata
                WHERE model_version = ?
            """
            
            cursor = self.conn.cursor()
            result = cursor.execute(query, (model_version,)).fetchone()
            
            if result:
                return json.loads(result[0])
            return None
        except Exception as e:
            logger.error(f"Error retrieving model metadata: {e}")
            raise
    
    def get_latest_model_version(self):
        """Get the latest model version from metadata."""
        try:
            query = """
                SELECT model_version
                FROM model_metadata
                ORDER BY training_date DESC
                LIMIT 1
            """
            
            cursor = self.conn.cursor()
            result = cursor.execute(query).fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error retrieving latest model version: {e}")
            raise
    
    def close(self):
        """Close SQLite connection."""
        if self.conn:
            self.conn.close()
            logger.info("Closed SQLite connection")

    def update_anomaly_score(self, timestamp, production_line, component_id, anomaly_score):
        """Update anomaly score for existing record."""
        try:
            query = """
                UPDATE sensor_readings 
                SET anomaly_score = ?
                WHERE timestamp = ? AND production_line = ? AND component_id = ?
            """
            
            cursor = self.conn.cursor()
            cursor.execute(query, (anomaly_score, timestamp, production_line, component_id))
            self.conn.commit()
            logger.info(f"Updated anomaly score for {production_line} - {component_id}")
        except Exception as e:
            logger.error(f"Error updating anomaly score: {e}")
            raise

def load_company_config():
    """Load company configuration from file."""
    try:
        print('Current working directory:', os.getcwd())
        print('Looking for:', os.path.abspath('config/company_config.json'))
        with open('config/company_config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading company config: {e}")
        return {} 