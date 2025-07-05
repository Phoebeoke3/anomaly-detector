"""
Dashboard Integration for Stream Processing

This module connects the stream processing results to the dashboard system,
allowing real-time display of windowing and anomaly detection results.
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import deque
import sqlite3
import os

class StreamDashboardIntegration:
    """Integrates stream processing results with the dashboard."""
    
    def __init__(self, db_path: str = "data/wind_turbine.db"):
        self.db_path = db_path
        self.stream_results = deque(maxlen=1000)  # Store last 1000 results
        self.window_statistics = {}
        self.anomaly_alerts = deque(maxlen=100)
        self.is_running = False
        self.thread = None
        
        # Initialize database tables for stream processing
        self._init_stream_tables()
    
    def _init_stream_tables(self):
        """Initialize database tables for stream processing data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create stream processing results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stream_windows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    production_line TEXT NOT NULL,
                    window_start TEXT NOT NULL,
                    window_end TEXT NOT NULL,
                    data_points INTEGER NOT NULL,
                    anomalies_detected INTEGER NOT NULL,
                    temperature_mean REAL,
                    temperature_std REAL,
                    humidity_mean REAL,
                    humidity_std REAL,
                    sound_mean REAL,
                    sound_std REAL,
                    processing_time REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create stream anomaly alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stream_anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    component_id TEXT NOT NULL,
                    sensor_id TEXT NOT NULL,
                    production_line TEXT NOT NULL,
                    anomaly_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    temperature REAL,
                    humidity REAL,
                    sound REAL,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create stream statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stream_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    messages_sent INTEGER NOT NULL,
                    messages_processed INTEGER NOT NULL,
                    anomalies_detected INTEGER NOT NULL,
                    windows_processed INTEGER NOT NULL,
                    processing_latency REAL,
                    active_windows TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Stream processing database tables initialized")
            
        except Exception as e:
            print(f"❌ Error initializing stream tables: {e}")
    
    def start(self):
        """Start the dashboard integration."""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._integration_worker, daemon=True)
            self.thread.start()
            print("✅ Stream dashboard integration started")
    
    def stop(self):
        """Stop the dashboard integration."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("🛑 Stream dashboard integration stopped")
    
    def add_window_result(self, window_result: Dict[str, Any]):
        """Add a window processing result."""
        self.stream_results.append({
            'type': 'window',
            'data': window_result,
            'timestamp': datetime.now().isoformat()
        })
        
        # Store in database
        self._store_window_result(window_result)
        
        # Update statistics
        production_line = window_result['production_line']
        if production_line not in self.window_statistics:
            self.window_statistics[production_line] = {
                'total_windows': 0,
                'total_anomalies': 0,
                'avg_processing_time': 0,
                'last_window': None
            }
        
        stats = self.window_statistics[production_line]
        stats['total_windows'] += 1
        stats['total_anomalies'] += len(window_result['anomalies'])
        stats['last_window'] = window_result
        stats['avg_processing_time'] = (
            (stats['avg_processing_time'] * (stats['total_windows'] - 1) + 
             window_result['processing_time']) / stats['total_windows']
        )
    
    def add_anomaly_alert(self, anomaly: Dict[str, Any]):
        """Add an anomaly alert."""
        self.anomaly_alerts.append({
            'type': 'anomaly',
            'data': anomaly,
            'timestamp': datetime.now().isoformat()
        })
        
        # Store in database
        self._store_anomaly_alert(anomaly)
    
    def add_system_statistics(self, stats: Dict[str, Any]):
        """Add system statistics."""
        self.stream_results.append({
            'type': 'statistics',
            'data': stats,
            'timestamp': datetime.now().isoformat()
        })
        
        # Store in database
        self._store_system_statistics(stats)
    
    def _store_window_result(self, window_result: Dict[str, Any]):
        """Store window result in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO stream_windows (
                    production_line, window_start, window_end, data_points,
                    anomalies_detected, temperature_mean, temperature_std,
                    humidity_mean, humidity_std, sound_mean, sound_std,
                    processing_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                window_result['production_line'],
                window_result['window_start'],
                window_result['window_end'],
                window_result['data_points'],
                len(window_result['anomalies']),
                window_result['statistics']['temperature']['mean'],
                window_result['statistics']['temperature']['std'],
                window_result['statistics']['humidity']['mean'],
                window_result['statistics']['humidity']['std'],
                window_result['statistics']['sound']['mean'],
                window_result['statistics']['sound']['std'],
                window_result['processing_time']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error storing window result: {e}")
    
    def _store_anomaly_alert(self, anomaly: Dict[str, Any]):
        """Store anomaly alert in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO stream_anomalies (
                    timestamp, component_id, sensor_id, production_line,
                    anomaly_type, severity, temperature, humidity, sound, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                anomaly['timestamp'],
                anomaly['component_id'],
                anomaly['sensor_id'],
                anomaly['production_line'],
                anomaly['anomaly_type'],
                anomaly['severity'],
                anomaly['details']['temperature'],
                anomaly['details']['humidity'],
                anomaly['details']['sound'],
                json.dumps(anomaly['details'])
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error storing anomaly alert: {e}")
    
    def _store_system_statistics(self, stats: Dict[str, Any]):
        """Store system statistics in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Handle both nested and flat statistics formats
            if 'summary' in stats and 'processor' in stats:
                # Nested format from SimpleStreamManager
                messages_sent = stats['summary']['total_messages_sent']
                messages_processed = stats['summary']['total_messages_processed']
                anomalies_detected = stats['summary']['total_anomalies_detected']
                windows_processed = stats['processor']['windows_processed']
                processing_latency = stats['processor']['average_processing_latency']
                active_windows = stats['processor']['active_windows']
            else:
                # Flat format from SimpleStreamProcessor
                messages_sent = stats.get('messages_sent', 0)
                messages_processed = stats.get('messages_processed', 0)
                anomalies_detected = stats.get('anomalies_detected', 0)
                windows_processed = stats.get('windows_processed', 0)
                processing_latency = stats.get('average_processing_latency', 0)
                active_windows = stats.get('active_windows', {})
            
            cursor.execute('''
                INSERT INTO stream_statistics (
                    messages_sent, messages_processed, anomalies_detected,
                    windows_processed, processing_latency, active_windows
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                messages_sent,
                messages_processed,
                anomalies_detected,
                windows_processed,
                processing_latency,
                json.dumps(active_windows)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error storing system statistics: {e}")
    
    def _integration_worker(self):
        """Worker thread for dashboard integration."""
        while self.is_running:
            try:
                # Clean up old data (keep last 24 hours)
                self._cleanup_old_data()
                time.sleep(60)  # Run cleanup every minute
                
            except Exception as e:
                print(f"❌ Error in integration worker: {e}")
                time.sleep(10)
    
    def _cleanup_old_data(self):
        """Clean up old data from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Keep only last 24 hours of data
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            cursor.execute('DELETE FROM stream_windows WHERE created_at < ?', (cutoff_time,))
            cursor.execute('DELETE FROM stream_anomalies WHERE created_at < ?', (cutoff_time,))
            cursor.execute('DELETE FROM stream_statistics WHERE created_at < ?', (cutoff_time,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error cleaning up old data: {e}")
    
    def get_stream_dashboard_data(self) -> Dict[str, Any]:
        """Get stream processing data for dashboard."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent window results
            cursor.execute('''
                SELECT * FROM stream_windows 
                ORDER BY created_at DESC 
                LIMIT 20
            ''')
            recent_windows = cursor.fetchall()
            
            # Get recent anomalies
            cursor.execute('''
                SELECT * FROM stream_anomalies 
                ORDER BY created_at DESC 
                LIMIT 50
            ''')
            recent_anomalies = cursor.fetchall()
            
            # Get latest statistics
            cursor.execute('''
                SELECT * FROM stream_statistics 
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
            latest_stats = cursor.fetchone()
            
            # Get window statistics by production line
            cursor.execute('''
                SELECT production_line, 
                       COUNT(*) as window_count,
                       SUM(anomalies_detected) as total_anomalies,
                       AVG(processing_time) as avg_processing_time
                FROM stream_windows 
                WHERE created_at > datetime('now', '-1 hour')
                GROUP BY production_line
            ''')
            hourly_stats = cursor.fetchall()
            
            conn.close()
            
            return {
                'recent_windows': recent_windows,
                'recent_anomalies': recent_anomalies,
                'latest_statistics': latest_stats,
                'hourly_statistics': hourly_stats,
                'window_statistics': self.window_statistics,
                'active_alerts': list(self.anomaly_alerts)[-10:],  # Last 10 alerts
                'stream_results': list(self.stream_results)[-20:]  # Last 20 results
            }
            
        except Exception as e:
            print(f"❌ Error getting stream dashboard data: {e}")
            return {}
    
    def get_stream_api_endpoints(self) -> Dict[str, Any]:
        """Get stream processing data for API endpoints."""
        dashboard_data = self.get_stream_dashboard_data()
        
        return {
            'stream_status': {
                'is_running': self.is_running,
                'total_windows_processed': sum(stats['total_windows'] for stats in self.window_statistics.values()),
                'total_anomalies_detected': sum(stats['total_anomalies'] for stats in self.window_statistics.values()),
                'active_production_lines': list(self.window_statistics.keys())
            },
            'recent_windows': dashboard_data.get('recent_windows', []),
            'recent_anomalies': dashboard_data.get('recent_anomalies', []),
            'window_statistics': self.window_statistics,
            'latest_alerts': dashboard_data.get('active_alerts', [])
        }


# Global instance for easy access
stream_integration = StreamDashboardIntegration() 