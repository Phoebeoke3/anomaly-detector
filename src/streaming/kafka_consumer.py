import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import threading
from collections import deque, defaultdict
import numpy as np
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WindowType(Enum):
    TIME = "time"
    COUNT = "count"
    SLIDING = "sliding"

@dataclass
class WindowConfig:
    """Configuration for stream processing windows."""
    window_type: WindowType
    size: int  # seconds for time windows, count for count windows
    slide: int = 1  # slide interval for sliding windows

class StreamProcessor:
    """Advanced stream processor with windowing and state management."""
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092',
                 topic: str = 'sensor-data',
                 group_id: str = 'anomaly-detector-group',
                 window_config: WindowConfig = None):
        """
        Initialize the stream processor.
        
        Args:
            bootstrap_servers: Kafka broker addresses
            topic: Kafka topic to consume from
            group_id: Consumer group ID for load balancing
            window_config: Configuration for windowing
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.window_config = window_config or WindowConfig(WindowType.TIME, 60)
        
        # Consumer
        self.consumer = None
        self.is_running = False
        self.consumer_thread = None
        
        # Window management
        self.windows = defaultdict(deque)  # production_line -> window_data
        self.window_timestamps = defaultdict(list)
        
        # State management
        self.state = {
            'processed_messages': 0,
            'windows_processed': 0,
            'anomalies_detected': 0,
            'last_processing_time': None,
            'processing_latency': deque(maxlen=100)
        }
        
        # Callbacks
        self.on_window_complete: Optional[Callable] = None
        self.on_anomaly_detected: Optional[Callable] = None
        
        self._initialize_consumer()
    
    def _initialize_consumer(self):
        """Initialize Kafka consumer with error handling."""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                max_poll_records=100,
                session_timeout_ms=30000,
                heartbeat_interval_ms=3000
            )
            logger.info(f"Kafka consumer initialized for topic: {self.topic}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {e}")
            raise
    
    def start(self):
        """Start the consumer thread."""
        if not self.is_running:
            self.is_running = True
            self.consumer_thread = threading.Thread(target=self._consumer_worker, daemon=True)
            self.consumer_thread.start()
            logger.info("Stream processor started")
    
    def stop(self):
        """Stop the consumer thread and close connections."""
        self.is_running = False
        if self.consumer_thread:
            self.consumer_thread.join(timeout=5)
        
        if self.consumer:
            self.consumer.close()
            logger.info("Stream processor stopped")
    
    def _consumer_worker(self):
        """Worker thread that consumes messages and processes windows."""
        while self.is_running:
            try:
                # Poll for messages with timeout
                message_batch = self.consumer.poll(timeout_ms=1000)
                
                for tp, messages in message_batch.items():
                    for message in messages:
                        self._process_message(message.value, message.key)
                
                # Process windows that are ready
                self._process_ready_windows()
                
            except Exception as e:
                logger.error(f"Error in consumer worker: {e}")
                time.sleep(1)
    
    def _process_message(self, message_data: Dict[str, Any], key: str):
        """Process a single message and add to appropriate window."""
        try:
            production_line = key or message_data.get('production_line', 'default')
            timestamp = datetime.fromisoformat(message_data['timestamp'])
            
            # Add to window
            self.windows[production_line].append({
                'data': message_data,
                'timestamp': timestamp
            })
            
            # Add timestamp for time-based windows
            if self.window_config.window_type == WindowType.TIME:
                self.window_timestamps[production_line].append(timestamp)
            
            # Update state
            self.state['processed_messages'] += 1
            
            logger.debug(f"Processed message for {production_line}: {message_data.get('component_id', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _process_ready_windows(self):
        """Process windows that are ready based on window configuration."""
        current_time = datetime.now()
        
        for production_line, window_data in self.windows.items():
            if self._is_window_ready(production_line, current_time):
                self._process_window(production_line, window_data)
    
    def _is_window_ready(self, production_line: str, current_time: datetime) -> bool:
        """Check if a window is ready for processing."""
        if self.window_config.window_type == WindowType.TIME:
            if not self.window_timestamps[production_line]:
                return False
            
            # Check if enough time has passed
            oldest_timestamp = self.window_timestamps[production_line][0]
            return (current_time - oldest_timestamp).total_seconds() >= self.window_config.size
        
        elif self.window_config.window_type == WindowType.COUNT:
            return len(self.windows[production_line]) >= self.window_config.size
        
        return False
    
    def _process_window(self, production_line: str, window_data: deque):
        """Process a complete window of data."""
        start_time = time.time()
        
        try:
            # Extract data from window
            data_points = [item['data'] for item in window_data]
            
            # Calculate window statistics
            window_stats = self._calculate_window_statistics(data_points)
            
            # Detect anomalies in the window
            anomalies = self._detect_window_anomalies(data_points, window_stats)
            
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
            
            # Call window completion callback
            if self.on_window_complete:
                self.on_window_complete(window_result)
            
            # Call anomaly detection callback
            if anomalies and self.on_anomaly_detected:
                for anomaly in anomalies:
                    self.on_anomaly_detected(anomaly)
            
            # Update state
            self.state['windows_processed'] += 1
            self.state['anomalies_detected'] += len(anomalies)
            self.state['last_processing_time'] = current_time
            self.state['processing_latency'].append(time.time() - start_time)
            
            # Clear processed window data
            self._clear_window(production_line)
            
            logger.info(f"Processed window for {production_line}: "
                       f"{len(data_points)} points, {len(anomalies)} anomalies")
            
        except Exception as e:
            logger.error(f"Error processing window for {production_line}: {e}")
    
    def _calculate_window_statistics(self, data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics for a window of data points."""
        if not data_points:
            return {}
        
        # Extract sensor values
        temperatures = [point['temperature'] for point in data_points]
        humidities = [point['humidity'] for point in data_points]
        sounds = [point['sound'] for point in data_points]
        
        # Calculate basic statistics
        stats = {
            'temperature': {
                'mean': np.mean(temperatures),
                'std': np.std(temperatures),
                'min': np.min(temperatures),
                'max': np.max(temperatures),
                'trend': self._calculate_trend(temperatures)
            },
            'humidity': {
                'mean': np.mean(humidities),
                'std': np.std(humidities),
                'min': np.min(humidities),
                'max': np.max(humidities),
                'trend': self._calculate_trend(humidities)
            },
            'sound': {
                'mean': np.mean(sounds),
                'std': np.std(sounds),
                'min': np.min(sounds),
                'max': np.max(sounds),
                'trend': self._calculate_trend(sounds)
            },
            'anomaly_count': sum(1 for point in data_points if point.get('is_anomaly', False)),
            'total_points': len(data_points)
        }
        
        return stats
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values."""
        if len(values) < 2:
            return 'stable'
        
        # Simple linear regression slope
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _detect_window_anomalies(self, data_points: List[Dict[str, Any]], 
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
                        'sound': point['sound'],
                        'expected_ranges': {
                            'temperature': [window_stats['temperature']['mean'] - 2*window_stats['temperature']['std'],
                                          window_stats['temperature']['mean'] + 2*window_stats['temperature']['std']],
                            'humidity': [window_stats['humidity']['mean'] - 2*window_stats['humidity']['std'],
                                       window_stats['humidity']['mean'] + 2*window_stats['humidity']['std']],
                            'sound': [window_stats['sound']['mean'] - 2*window_stats['sound']['std'],
                                    window_stats['sound']['mean'] + 2*window_stats['sound']['std']]
                        }
                    }
                }
                anomalies.append(anomaly)
            
            # Check for known anomalies (from simulation)
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
        if self.window_config.window_type == WindowType.TIME:
            # Remove data points that are older than window size
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(seconds=self.window_config.size)
            
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
        
        else:  # COUNT window
            # Remove oldest data points to maintain window size
            while len(self.windows[production_line]) > self.window_config.size:
                self.windows[production_line].popleft()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get stream processor statistics."""
        avg_latency = np.mean(self.state['processing_latency']) if self.state['processing_latency'] else 0
        
        return {
            'processed_messages': self.state['processed_messages'],
            'windows_processed': self.state['windows_processed'],
            'anomalies_detected': self.state['anomalies_detected'],
            'average_processing_latency': avg_latency,
            'last_processing_time': self.state['last_processing_time'],
            'active_windows': {line: len(data) for line, data in self.windows.items()},
            'window_config': {
                'type': self.window_config.window_type.value,
                'size': self.window_config.size,
                'slide': self.window_config.slide
            }
        } 