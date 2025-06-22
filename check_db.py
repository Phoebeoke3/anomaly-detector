import sqlite3
import pandas as pd
from datetime import datetime

def check_database():
    """Check the database structure and content."""
    try:
        # Connect to database
        conn = sqlite3.connect('semiconductor.db')
        cursor = conn.cursor()
        
        print("=== DATABASE STRUCTURE ===")
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"Tables found: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            print(f"    Columns:")
            for col in columns:
                print(f"      {col[1]} ({col[2]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"    Row count: {count}")
            
            # Show sample data if table has data
            if count > 0:
                cursor.execute(f"SELECT * FROM {table[0]} LIMIT 3")
                sample_data = cursor.fetchall()
                print(f"    Sample data:")
                for row in sample_data:
                    print(f"      {row}")
            print()
        
        # Check for sensor_readings table specifically
        if any('sensor_readings' in table for table in tables):
            print("=== SENSOR READINGS DETAILS ===")
            
            # Get latest readings
            cursor.execute("""
                SELECT timestamp, sensor_id, temperature, humidity, sound_level, anomaly_score, prediction
                FROM sensor_readings 
                ORDER BY timestamp DESC 
                LIMIT 5
            """)
            latest = cursor.fetchall()
            
            print("Latest 5 sensor readings:")
            for row in latest:
                print(f"  {row}")
            
            # Get statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_readings,
                    MIN(timestamp) as earliest,
                    MAX(timestamp) as latest,
                    AVG(temperature) as avg_temp,
                    AVG(humidity) as avg_humidity,
                    AVG(sound_level) as avg_sound,
                    AVG(anomaly_score) as avg_anomaly_score
                FROM sensor_readings
            """)
            stats = cursor.fetchone()
            
            print(f"\nStatistics:")
            print(f"  Total readings: {stats[0]}")
            print(f"  Time range: {stats[1]} to {stats[2]}")
            print(f"  Average temperature: {stats[3]:.2f}°C")
            print(f"  Average humidity: {stats[4]:.2f}%")
            print(f"  Average sound level: {stats[5]:.2f} dB")
            print(f"  Average anomaly score: {stats[6]:.4f}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_database() 