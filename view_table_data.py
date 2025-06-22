import sqlite3
import pandas as pd
from datetime import datetime

def view_table_data(table_name=None, limit=20):
    """View data stored in database tables."""
    try:
        # Connect to database
        conn = sqlite3.connect('semiconductor.db')
        
        # Get all tables if no specific table is specified
        if table_name is None:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print("Available tables:")
            for table in tables:
                print(f"  - {table[0]}")
            print()
            
            # Show data from each table
            for table in tables:
                table_name = table[0]
                print(f"\n{'='*60}")
                print(f"TABLE: {table_name}")
                print(f"{'='*60}")
                view_single_table(conn, table_name, limit)
        else:
            view_single_table(conn, table_name, limit)
        
        conn.close()
        
    except Exception as e:
        print(f"Error viewing table data: {e}")

def view_single_table(conn, table_name, limit):
    """View data from a specific table."""
    try:
        # Get table schema
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"Schema:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"\nTotal rows: {count}")
        
        if count == 0:
            print("No data found in this table.")
            return
        
        # Get data
        df = pd.read_sql_query(f"SELECT * FROM {table_name} ORDER BY 1 DESC LIMIT {limit}", conn)
        
        print(f"\nShowing latest {len(df)} rows:")
        print("-" * 80)
        
        # Display data in a formatted way
        if table_name == 'sensor_readings':
            # Format sensor readings nicely
            for _, row in df.iterrows():
                print(f"ID: {row['id']:3d} | {row['timestamp']} | {row['sensor_id']:12s} | "
                      f"Temp: {row['temperature']:5.1f}°C | Humidity: {row['humidity']:5.1f}% | "
                      f"Sound: {row['sound_level']:5.1f}dB | Score: {row['anomaly_score']:6.4f} | {row['prediction']}")
        else:
            # Display other tables in a simple format
            print(df.to_string(index=False))
        
        # Show more options if there are more rows
        if count > limit:
            print(f"\n... and {count - limit} more rows")
            print(f"To see more data, increase the limit parameter")
        
    except Exception as e:
        print(f"Error viewing table {table_name}: {e}")

def view_sensor_data_detailed():
    """View detailed sensor data with statistics."""
    try:
        conn = sqlite3.connect('semiconductor.db')
        
        print("\n" + "="*80)
        print("DETAILED SENSOR DATA ANALYSIS")
        print("="*80)
        
        # Get sensor data with statistics
        query = """
        SELECT 
            sensor_id,
            COUNT(*) as readings,
            AVG(temperature) as avg_temp,
            MIN(temperature) as min_temp,
            MAX(temperature) as max_temp,
            AVG(humidity) as avg_humidity,
            MIN(humidity) as min_humidity,
            MAX(humidity) as max_humidity,
            AVG(sound_level) as avg_sound,
            MIN(sound_level) as min_sound,
            MAX(sound_level) as max_sound,
            AVG(anomaly_score) as avg_score,
            MIN(anomaly_score) as min_score,
            MAX(anomaly_score) as max_score
        FROM sensor_readings
        GROUP BY sensor_id
        ORDER BY readings DESC
        """
        
        df = pd.read_sql_query(query, conn)
        
        print("\nSensor Statistics by Sensor ID:")
        print("-" * 80)
        
        for _, row in df.iterrows():
            print(f"\nSensor: {row['sensor_id']}")
            print(f"  Readings: {row['readings']:,}")
            print(f"  Temperature: {row['avg_temp']:.2f}°C (range: {row['min_temp']:.1f}°C - {row['max_temp']:.1f}°C)")
            print(f"  Humidity: {row['avg_humidity']:.2f}% (range: {row['min_humidity']:.1f}% - {row['max_humidity']:.1f}%)")
            print(f"  Sound Level: {row['avg_sound']:.2f} dB (range: {row['min_sound']:.1f} dB - {row['max_sound']:.1f} dB)")
            print(f"  Anomaly Score: {row['avg_score']:.4f} (range: {row['min_score']:.4f} - {row['max_score']:.4f})")
        
        # Get prediction distribution
        query = """
        SELECT 
            prediction,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sensor_readings), 1) as percentage
        FROM sensor_readings
        GROUP BY prediction
        ORDER BY count DESC
        """
        
        df_pred = pd.read_sql_query(query, conn)
        
        print(f"\nPrediction Distribution:")
        print("-" * 40)
        for _, row in df_pred.iterrows():
            print(f"  {row['prediction']:10s}: {row['count']:4d} readings ({row['percentage']:5.1f}%)")
        
        conn.close()
        
    except Exception as e:
        print(f"Error in detailed analysis: {e}")

if __name__ == "__main__":
    print("DATABASE TABLE VIEWER")
    print("=" * 50)
    
    # View all tables
    view_table_data()
    
    # Show detailed sensor analysis
    view_sensor_data_detailed()
    
    print(f"\n" + "="*50)
    print("To view specific table with custom limit:")
    print("  view_table_data('sensor_readings', 50)  # Show 50 rows")
    print("  view_table_data('model_metadata')       # Show model metadata") 