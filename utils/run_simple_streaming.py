#!/usr/bin/env python3
"""
Simple Stream Processing Runner for IoT Anomaly Detection

This script demonstrates advanced stream processing capabilities without requiring Kafka.
It uses in-memory queues and threading to simulate a production stream processing system.
Perfect for development, testing, and demonstrations.
"""

import sys
import os
import time
import signal
import argparse
import threading
import queue
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List
from collections import deque, defaultdict

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("\n🛑 Received shutdown signal. Stopping stream processing...")
    if hasattr(signal_handler, 'stream_processor'):
        signal_handler.stream_processor.stop()
    sys.exit(0)

class SimpleSensorSimulator:
    """Simple sensor data simulator with realistic patterns."""
    
    def __init__(self, data_queue: queue.Queue, interval: float = 1.0, anomaly_prob: float = 0.05):
        self.data_queue = data_queue
        self.interval = interval
        self.anomaly_prob = anomaly_prob
        self.is_running = False
        self.thread = None
        self.messages_sent = 0
        
        # Simulation parameters
        self.trend_duration = 300  # 5 minutes
        self.seasonal_period = 3600  # 1 hour
        self.start_time = time.time()
    
    def start(self):
        """Start the simulation."""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._simulation_worker, daemon=True)
            self.thread.start()
            print("✅ Sensor simulation started")
    
    def stop(self):
        """Stop the simulation."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("🛑 Sensor simulation stopped")
    
    def _simulation_worker(self):
        """Worker thread for continuous sensor data generation."""
        while self.is_running:
            try:
                # Generate realistic sensor data
                sensor_data = self._generate_realistic_data()
                
                # Add to queue
                self.data_queue.put(sensor_data)
                self.messages_sent += 1
                
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"❌ Error in simulation: {e}")
                time.sleep(self.interval)
    
    def _generate_realistic_data(self) -> Dict[str, Any]:
        """Generate realistic sensor data with trends, seasonality, and anomalies."""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        # Base values with trends and seasonality
        base_temp = 25 + 5 * np.sin(2 * np.pi * elapsed_time / self.seasonal_period)
        base_humidity = 50 + 10 * np.cos(2 * np.pi * elapsed_time / self.seasonal_period)
        base_sound = 65 + 5 * np.sin(2 * np.pi * elapsed_time / (self.seasonal_period / 2))
        
        # Add gradual trends
        trend_temp = 0.1 * np.sin(2 * np.pi * elapsed_time / self.trend_duration)
        trend_humidity = -0.05 * np.cos(2 * np.pi * elapsed_time / self.trend_duration)
        
        # Add noise
        noise_temp = random.gauss(0, 1)
        noise_humidity = random.gauss(0, 2)
        noise_sound = random.gauss(0, 1.5)
        
        # Determine if this should be an anomaly
        is_anomaly = random.random() < self.anomaly_prob
        
        if is_anomaly:
            # Inject anomaly
            anomaly_type = random.choice(['spike', 'drift', 'noise'])
            if anomaly_type == 'spike':
                noise_temp += random.gauss(0, 10)
                noise_humidity += random.gauss(0, 15)
                noise_sound += random.gauss(0, 20)
            elif anomaly_type == 'drift':
                trend_temp += 5
                trend_humidity += 10
            else:  # noise
                noise_temp += random.gauss(0, 5)
                noise_humidity += random.gauss(0, 8)
                noise_sound += random.gauss(0, 12)
        
        # Calculate final values
        temperature = base_temp + trend_temp + noise_temp
        humidity = base_humidity + trend_humidity + noise_humidity
        sound = base_sound + noise_sound
        
        # Ensure values are within realistic bounds
        temperature = max(10, min(40, temperature))
        humidity = max(20, min(80, humidity))
        sound = max(40, min(90, sound))
        
        return {
            'timestamp': datetime.now().isoformat(),
            'temperature': round(temperature, 2),
            'humidity': round(humidity, 2),
            'sound': round(sound, 2),
            'production_line': random.choice(['blade_production', 'nacelle_assembly']),
            'component_id': f"comp_{random.randint(1000, 9999)}",
            'sensor_id': f"sensor_{random.randint(1, 10)}",
            'is_anomaly': is_anomaly,
            'anomaly_type': anomaly_type if is_anomaly else None,
            'batch_id': f"batch_{int(elapsed_time / 60)}"
        }

class SimpleStreamProcessor:
    """Simple stream processor with windowing and anomaly detection."""
    
    def __init__(self, data_queue: queue.Queue, window_size: int = 60, window_type: str = 'time'):
        self.data_queue = data_queue
        self.window_size = window_size
        self.window_type = window_type
        self.is_running = False
        self.thread = None
        
        # Window management
        self.windows = defaultdict(deque)  # production_line -> window_data
        self.window_timestamps = defaultdict(list)
        
        # Statistics
        self.messages_processed = 0
        self.windows_processed = 0
        self.anomalies_detected = 0
        self.processing_latency = deque(maxlen=100)
        
        # Alert handlers
        self.alert_handlers = []
    
    def start(self):
        """Start the stream processor."""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._processing_worker, daemon=True)
            self.thread.start()
            print("✅ Stream processor started")
    
    def stop(self):
        """Stop the stream processor."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("🛑 Stream processor stopped")
    
    def add_alert_handler(self, handler):
        """Add an alert handler."""
        self.alert_handlers.append(handler)
    
    def _processing_worker(self):
        """Worker thread for processing data streams."""
        while self.is_running:
            try:
                # Get data from queue with timeout
                try:
                    data = self.data_queue.get(timeout=1.0)
                    self._process_message(data)
                except queue.Empty:
                    # No data available, check if windows are ready
                    self._process_ready_windows()
                    continue
                
                # Process windows that are ready
                self._process_ready_windows()
                
            except Exception as e:
                print(f"❌ Error in processing: {e}")
                time.sleep(1)
    
    def _process_message(self, data: Dict[str, Any]):
        """Process a single message."""
        start_time = time.time()
        
        try:
            production_line = data['production_line']
            timestamp = datetime.fromisoformat(data['timestamp'])
            
            # Add to window
            self.windows[production_line].append({
                'data': data,
                'timestamp': timestamp
            })
            
            # Add timestamp for time-based windows
            if self.window_type == 'time':
                self.window_timestamps[production_line].append(timestamp)
            
            self.messages_processed += 1
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
    
    def _process_ready_windows(self):
        """Process windows that are ready."""
        current_time = datetime.now()
        
        for production_line, window_data in self.windows.items():
            if self._is_window_ready(production_line, current_time):
                self._process_window(production_line, window_data)
    
    def _is_window_ready(self, production_line: str, current_time: datetime) -> bool:
        """Check if a window is ready for processing."""
        if self.window_type == 'time':
            if not self.window_timestamps[production_line]:
                return False
            
            # Check if enough time has passed
            oldest_timestamp = self.window_timestamps[production_line][0]
            return (current_time - oldest_timestamp).total_seconds() >= self.window_size
        
        else:  # count
            return len(self.windows[production_line]) >= self.window_size
    
    def _process_window(self, production_line: str, window_data: deque):
        """Process a complete window of data."""
        start_time = time.time()
        
        try:
            # Extract data from window
            data_points = [item['data'] for item in window_data]
            
            # Calculate window statistics
            window_stats = self._calculate_window_statistics(data_points)
            
            # Detect anomalies
            anomalies = self._detect_anomalies(data_points, window_stats)
            
            # Create window result
            window_result = {
                'production_line': production_line,
                'window_start': window_data[0]['timestamp'].isoformat(),
                'window_end': window_data[-1]['timestamp'].isoformat(),
                'data_points': len(data_points),
                'statistics': window_stats,
                'anomalies': anomalies,
                'processing_time': time.time() - start_time
            }
            
            # Trigger alerts for anomalies
            for anomaly in anomalies:
                for handler in self.alert_handlers:
                    try:
                        handler(anomaly)
                    except Exception as e:
                        print(f"❌ Error in alert handler: {e}")
            
            # Update statistics
            self.windows_processed += 1
            self.anomalies_detected += len(anomalies)
            self.processing_latency.append(time.time() - start_time)
            
            # Clear processed window data
            self._clear_window(production_line)
            
            print(f"📊 Processed window for {production_line}: "
                  f"{len(data_points)} points, {len(anomalies)} anomalies")
            
        except Exception as e:
            print(f"❌ Error processing window: {e}")
    
    def _calculate_window_statistics(self, data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics for a window of data points."""
        if not data_points:
            return {}
        
        temperatures = [point['temperature'] for point in data_points]
        humidities = [point['humidity'] for point in data_points]
        sounds = [point['sound'] for point in data_points]
        
        return {
            'temperature': {
                'mean': np.mean(temperatures),
                'std': np.std(temperatures),
                'min': np.min(temperatures),
                'max': np.max(temperatures)
            },
            'humidity': {
                'mean': np.mean(humidities),
                'std': np.std(humidities),
                'min': np.min(humidities),
                'max': np.max(humidities)
            },
            'sound': {
                'mean': np.mean(sounds),
                'std': np.std(sounds),
                'min': np.min(sounds),
                'max': np.max(sounds)
            },
            'anomaly_count': sum(1 for point in data_points if point.get('is_anomaly', False)),
            'total_points': len(data_points)
        }
    
    def _detect_anomalies(self, data_points: List[Dict[str, Any]], 
                         window_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in a window of data points."""
        anomalies = []
        
        for point in data_points:
            # Check for statistical outliers
            if self._is_statistical_outlier(point, window_stats):
                anomaly = {
                    'timestamp': point['timestamp'],
                    'component_id': point['component_id'],
                    'sensor_id': point['sensor_id'],
                    'production_line': point['production_line'],
                    'anomaly_type': 'statistical_outlier',
                    'severity': 'high' if point.get('is_anomaly', False) else 'medium',
                    'details': {
                        'temperature': point['temperature'],
                        'humidity': point['humidity'],
                        'sound': point['sound']
                    }
                }
                anomalies.append(anomaly)
            
            # Check for known anomalies
            elif point.get('is_anomaly', False):
                anomaly = {
                    'timestamp': point['timestamp'],
                    'component_id': point['component_id'],
                    'sensor_id': point['sensor_id'],
                    'production_line': point['production_line'],
                    'anomaly_type': point.get('anomaly_type', 'unknown'),
                    'severity': 'high',
                    'details': {
                        'temperature': point['temperature'],
                        'humidity': point['humidity'],
                        'sound': point['sound'],
                        'simulated_anomaly': True
                    }
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    def _is_statistical_outlier(self, point: Dict[str, Any], 
                               window_stats: Dict[str, Any]) -> bool:
        """Check if a data point is a statistical outlier."""
        temp = point['temperature']
        humidity = point['humidity']
        sound = point['sound']
        
        # Check if any sensor value is outside 2 standard deviations
        temp_outlier = abs(temp - window_stats['temperature']['mean']) > 2 * window_stats['temperature']['std']
        humidity_outlier = abs(humidity - window_stats['humidity']['mean']) > 2 * window_stats['humidity']['std']
        sound_outlier = abs(sound - window_stats['sound']['mean']) > 2 * window_stats['sound']['std']
        
        return temp_outlier or humidity_outlier or sound_outlier
    
    def _clear_window(self, production_line: str):
        """Clear processed window data."""
        if self.window_type == 'time':
            # Remove data points that are older than window size
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(seconds=self.window_size)
            
            # Remove old timestamps
            self.window_timestamps[production_line] = [
                ts for ts in self.window_timestamps[production_line] 
                if ts > cutoff_time
            ]
            
            # Remove old data points
            self.windows[production_line] = deque([
                item for item in self.windows[production_line]
                if item['timestamp'] > cutoff_time
            ])
        
        else:  # count window
            # Remove oldest data points to maintain window size
            while len(self.windows[production_line]) > self.window_size:
                self.windows[production_line].popleft()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get stream processor statistics."""
        avg_latency = np.mean(self.processing_latency) if self.processing_latency else 0
        
        return {
            'messages_processed': self.messages_processed,
            'windows_processed': self.windows_processed,
            'anomalies_detected': self.anomalies_detected,
            'average_processing_latency': avg_latency,
            'active_windows': {line: len(data) for line, data in self.windows.items()}
        }

class SimpleStreamManager:
    """Simple stream processing manager."""
    
    def __init__(self, window_size: int = 60, window_type: str = 'time', 
                 simulation_interval: float = 1.0, anomaly_probability: float = 0.05):
        self.window_size = window_size
        self.window_type = window_type
        self.simulation_interval = simulation_interval
        self.anomaly_probability = anomaly_probability
        
        # Create data queue
        self.data_queue = queue.Queue(maxsize=1000)
        
        # Create components
        self.simulator = SimpleSensorSimulator(
            self.data_queue, 
            interval=simulation_interval,
            anomaly_prob=anomaly_probability
        )
        
        self.processor = SimpleStreamProcessor(
            self.data_queue,
            window_size=window_size,
            window_type=window_type
        )
        
        # Add default alert handlers
        self.processor.add_alert_handler(self._console_alert_handler)
        
        self.is_running = False
    
    def start(self):
        """Start the stream processing system."""
        if not self.is_running:
            self.is_running = True
            self.simulator.start()
            self.processor.start()
            print("✅ Simple stream processing system started")
    
    def stop(self):
        """Stop the stream processing system."""
        self.is_running = False
        self.simulator.stop()
        self.processor.stop()
        print("🛑 Simple stream processing system stopped")
    
    def add_alert_handler(self, handler):
        """Add a custom alert handler."""
        self.processor.add_alert_handler(handler)
    
    def _console_alert_handler(self, anomaly: Dict[str, Any]):
        """Default console alert handler."""
        print(f"🚨 ALERT: {anomaly['anomaly_type']} anomaly detected!")
        print(f"   Component: {anomaly['component_id']}")
        print(f"   Production Line: {anomaly['production_line']}")
        print(f"   Severity: {anomaly['severity']}")
        print(f"   Timestamp: {anomaly['timestamp']}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics."""
        processor_stats = self.processor.get_statistics()
        
        return {
            'system': {
                'status': 'running' if self.is_running else 'stopped',
                'window_type': self.window_type,
                'window_size': self.window_size
            },
            'simulator': {
                'messages_sent': self.simulator.messages_sent
            },
            'processor': processor_stats,
            'summary': {
                'total_messages_sent': self.simulator.messages_sent,
                'total_messages_processed': processor_stats['messages_processed'],
                'total_anomalies_detected': processor_stats['anomalies_detected']
            }
        }

def main():
    """Main function to run the simple stream processing system."""
    parser = argparse.ArgumentParser(description='Simple Stream Processing for IoT Anomaly Detection')
    parser.add_argument('--window-type', choices=['time', 'count'], default='time',
                       help='Window type for stream processing (default: time)')
    parser.add_argument('--window-size', type=int, default=60,
                       help='Window size in seconds (time) or count (count) (default: 60)')
    parser.add_argument('--simulation-interval', type=float, default=1.0,
                       help='Sensor data simulation interval in seconds (default: 1.0)')
    parser.add_argument('--anomaly-probability', type=float, default=0.05,
                       help='Probability of anomaly injection (default: 0.05)')
    
    args = parser.parse_args()
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 Starting Simple Stream Processing System")
    print("=" * 60)
    print(f"Window Type: {args.window_type}")
    print(f"Window Size: {args.window_size}")
    print(f"Simulation Interval: {args.simulation_interval}s")
    print(f"Anomaly Probability: {args.anomaly_probability}")
    print("=" * 60)
    
    try:
        # Create and start stream manager
        stream_manager = SimpleStreamManager(
            window_size=args.window_size,
            window_type=args.window_type,
            simulation_interval=args.simulation_interval,
            anomaly_probability=args.anomaly_probability
        )
        
        # Store reference for signal handler
        signal_handler.stream_processor = stream_manager
        
        # Start the system
        stream_manager.start()
        
        print("✅ Stream processing system started successfully!")
        print("📊 Monitoring system statistics...")
        print("Press Ctrl+C to stop")
        
        # Monitor and display statistics
        while True:
            time.sleep(10)  # Update every 10 seconds
            
            # Get and display statistics
            stats = stream_manager.get_statistics()
            
            # Only display if there's activity
            if stats['summary']['total_messages_processed'] > 0:
                print(f"\n📈 System Statistics ({datetime.now().strftime('%H:%M:%S')})")
                print("-" * 40)
                print(f"Status: {stats['system']['status']}")
                print(f"Messages Sent: {stats['summary']['total_messages_sent']}")
                print(f"Messages Processed: {stats['summary']['total_messages_processed']}")
                print(f"Anomalies Detected: {stats['summary']['total_anomalies_detected']}")
                print(f"Windows Processed: {stats['processor']['windows_processed']}")
                print(f"Processing Latency: {stats['processor']['average_processing_latency']:.3f}s")
                
                # Display active windows
                active_windows = stats['processor']['active_windows']
                if active_windows:
                    print(f"Active Windows: {active_windows}")
                
                print("-" * 40)
    
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal")
    except Exception as e:
        print(f"❌ Error running stream processing system: {e}")
        return 1
    finally:
        # Cleanup
        if 'stream_manager' in locals():
            stream_manager.stop()
        print("👋 Stream processing system stopped")

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 