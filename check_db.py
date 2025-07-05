#!/usr/bin/env python3
import sqlite3

def check_stream_tables():
    conn = sqlite3.connect('data/wind_turbine.db')
    cursor = conn.cursor()
    
    # Check stream tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'stream%'")
    stream_tables = cursor.fetchall()
    print("Stream tables:", stream_tables)
    
    # Check stream_statistics table structure
    cursor.execute("PRAGMA table_info(stream_statistics)")
    columns = cursor.fetchall()
    print("\nStream statistics table structure:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Check stream_statistics table
    cursor.execute("SELECT COUNT(*) FROM stream_statistics")
    stats_count = cursor.fetchone()[0]
    print(f"\nStream stats count: {stats_count}")
    
    if stats_count > 0:
        cursor.execute("SELECT * FROM stream_statistics ORDER BY created_at DESC LIMIT 1")
        latest_stats = cursor.fetchone()
        print("Latest stats:", latest_stats)
        
        # Show column names with values
        column_names = [col[1] for col in columns]
        print("\nLatest stats breakdown:")
        for i, (name, value) in enumerate(zip(column_names, latest_stats)):
            print(f"  {name}: {value}")
    
    # Check stream_windows table
    cursor.execute("SELECT COUNT(*) FROM stream_windows")
    windows_count = cursor.fetchone()[0]
    print(f"\nStream windows count: {windows_count}")
    
    # Check stream_anomalies table
    cursor.execute("SELECT COUNT(*) FROM stream_anomalies")
    anomalies_count = cursor.fetchone()[0]
    print(f"Stream anomalies count: {anomalies_count}")
    
    conn.close()

if __name__ == "__main__":
    check_stream_tables() 