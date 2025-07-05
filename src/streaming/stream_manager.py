import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import threading
from dataclasses import dataclass
from enum import Enum

from .kafka_producer import SensorDataProducer, AdvancedSensorSimulator
from .kafka_consumer import StreamProcessor, WindowConfig, WindowType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamProcessingMode(Enum):
    REAL_TIME = "real_time"
    BATCH = "batch"
    HYBRID = "hybrid"

@dataclass
class StreamConfig:
    """Configuration for the stream processing system."""
    kafka_bootstrap_servers: str = 'localhost:9092'
    sensor_data_topic: str = 'sensor-data'
    anomaly_alerts_topic: str = 'anomaly-alerts'
    consumer_group_id: str = 'anomaly-detector-group'
    
    # Window configuration
    window_type: WindowType = WindowType.TIME
    window_size: int = 60  # seconds for time windows
    window_slide: int = 30  # slide interval
    
    # Producer configuration
    max_queue_size: int = 1000
    batch_size: int = 100
    linger_ms: int = 100
    
    # Processing mode
    processing_mode: StreamProcessingMode = StreamProcessingMode.REAL_TIME
    
    # Simulation configuration
    simulation_interval: float = 1.0
    anomaly_probability: float = 0.05

class StreamManager:
    """Advanced stream processing manager for IoT anomaly detection."""
    
    def __init__(self, config: StreamConfig):
        """
        Initialize the stream processing manager.
        
        Args:
            config: Stream processing configuration
        """
        self.config = config
        self.is_running = False
        
        # Components
        self.producer: Optional[SensorDataProducer] = None
        self.consumer: Optional[StreamProcessor] = None
        self.simulator: Optional[AdvancedSensorSimulator] = None
        
        # Threads
        self.manager_thread: Optional[threading.Thread] = None
        
        # Statistics and monitoring
        self.statistics = {
            'start_time': None,
            'total_messages_produced': 0,
            'total_messages_consumed': 0,
            'total_anomalies_detected': 0,
            'system_health': 'healthy',
            'last_heartbeat': None
        }
        
        # Alert handlers
        self.alert_handlers: List[callable] = []
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all stream processing components."""
        try:
            # Initialize producer
            self.producer = SensorDataProducer(
                bootstrap_servers=self.config.kafka_bootstrap_servers,
                topic=self.config.sensor_data_topic,
                max_queue_size=self.config.max_queue_size,
                batch_size=self.config.batch_size,
                linger_ms=self.config.linger_ms
            )
            
            # Initialize consumer with windowing
            window_config = WindowConfig(
                window_type=self.config.window_type,
                size=self.config.window_size,
                slide=self.config.window_slide
            )
            
            self.consumer = StreamProcessor(
                bootstrap_servers=self.config.kafka_bootstrap_servers,
                topic=self.config.sensor_data_topic,
                group_id=self.config.consumer_group_id,
                window_config=window_config
            )
            
            # Initialize simulator
            self.simulator = AdvancedSensorSimulator(self.producer)
            self.simulator.anomaly_probability = self.config.anomaly_probability
            
            # Set up callbacks
            self.consumer.on_window_complete = self._on_window_complete
            self.consumer.on_anomaly_detected = self._on_anomaly_detected
            
            logger.info("Stream processing components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize stream processing components: {e}")
            raise
    
    def start(self):
        """Start the stream processing system."""
        if self.is_running:
            logger.warning("Stream manager is already running")
            return
        
        try:
            # Start components
            self.producer.start()
            self.consumer.start()
            self.simulator.start_simulation(self.config.simulation_interval)
            
            # Start manager thread for monitoring
            self.is_running = True
            self.manager_thread = threading.Thread(target=self._manager_worker, daemon=True)
            self.manager_thread.start()
            
            # Update statistics
            self.statistics['start_time'] = datetime.now()
            self.statistics['last_heartbeat'] = datetime.now()
            
            logger.info("Stream processing system started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start stream processing system: {e}")
            self.stop()
            raise
    
    def stop(self):
        """Stop the stream processing system."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Stop components
        if self.simulator:
            self.simulator.stop_simulation()
        
        if self.consumer:
            self.consumer.stop()
        
        if self.producer:
            self.producer.stop()
        
        # Wait for manager thread
        if self.manager_thread:
            self.manager_thread.join(timeout=5)
        
        logger.info("Stream processing system stopped")
    
    def _manager_worker(self):
        """Manager worker thread for monitoring and health checks."""
        while self.is_running:
            try:
                # Update heartbeat
                self.statistics['last_heartbeat'] = datetime.now()
                
                # Collect statistics from components
                producer_stats = self.producer.get_statistics()
                consumer_stats = self.consumer.get_statistics()
                
                # Update global statistics
                self.statistics['total_messages_produced'] = producer_stats['messages_sent']
                self.statistics['total_messages_consumed'] = consumer_stats['processed_messages']
                self.statistics['total_anomalies_detected'] = consumer_stats['anomalies_detected']
                
                # Health check
                self._perform_health_check(producer_stats, consumer_stats)
                
                # Log periodic statistics
                if self.statistics['total_messages_consumed'] % 100 == 0:
                    logger.info(f"Stream processing statistics: "
                              f"Produced: {self.statistics['total_messages_produced']}, "
                              f"Consumed: {self.statistics['total_messages_consumed']}, "
                              f"Anomalies: {self.statistics['total_anomalies_detected']}")
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in manager worker: {e}")
                time.sleep(5)
    
    def _perform_health_check(self, producer_stats: Dict[str, Any], 
                            consumer_stats: Dict[str, Any]):
        """Perform system health check."""
        health_issues = []
        
        # Check producer health
        if producer_stats['errors'] > 10:
            health_issues.append("High producer error rate")
        
        if producer_stats['success_rate'] < 0.95:
            health_issues.append("Low producer success rate")
        
        # Check consumer health
        if consumer_stats['processed_messages'] == 0:
            health_issues.append("No messages being consumed")
        
        # Check processing latency
        if consumer_stats['average_processing_latency'] > 1.0:
            health_issues.append("High processing latency")
        
        # Update system health
        if health_issues:
            self.statistics['system_health'] = 'degraded'
            logger.warning(f"System health issues detected: {', '.join(health_issues)}")
        else:
            self.statistics['system_health'] = 'healthy'
    
    def _on_window_complete(self, window_result: Dict[str, Any]):
        """Callback for completed window processing."""
        try:
            logger.info(f"Window completed for {window_result['production_line']}: "
                       f"{window_result['data_points']} points, "
                       f"{len(window_result['anomalies'])} anomalies")
            
            # Store window result for analysis
            self._store_window_result(window_result)
            
        except Exception as e:
            logger.error(f"Error handling window completion: {e}")
    
    def _on_anomaly_detected(self, anomaly: Dict[str, Any]):
        """Callback for detected anomalies."""
        try:
            logger.warning(f"Anomaly detected: {anomaly['anomaly_type']} "
                          f"for {anomaly['component_id']} on {anomaly['production_line']}")
            
            # Trigger alert handlers
            for handler in self.alert_handlers:
                try:
                    handler(anomaly)
                except Exception as e:
                    logger.error(f"Error in alert handler: {e}")
            
            # Store anomaly for analysis
            self._store_anomaly(anomaly)
            
        except Exception as e:
            logger.error(f"Error handling anomaly detection: {e}")
    
    def _store_window_result(self, window_result: Dict[str, Any]):
        """Store window processing result for analysis."""
        # This could be implemented to store in a database or file
        # For now, we'll just log it
        pass
    
    def _store_anomaly(self, anomaly: Dict[str, Any]):
        """Store detected anomaly for analysis."""
        # This could be implemented to store in a database or file
        # For now, we'll just log it
        pass
    
    def add_alert_handler(self, handler: callable):
        """Add a custom alert handler for anomalies."""
        self.alert_handlers.append(handler)
        logger.info("Alert handler added")
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        producer_stats = self.producer.get_statistics() if self.producer else {}
        consumer_stats = self.consumer.get_statistics() if self.consumer else {}
        
        uptime = None
        if self.statistics['start_time']:
            uptime = (datetime.now() - self.statistics['start_time']).total_seconds()
        
        return {
            'system': {
                'status': 'running' if self.is_running else 'stopped',
                'health': self.statistics['system_health'],
                'uptime_seconds': uptime,
                'last_heartbeat': self.statistics['last_heartbeat']
            },
            'producer': producer_stats,
            'consumer': consumer_stats,
            'summary': {
                'total_messages_produced': self.statistics['total_messages_produced'],
                'total_messages_consumed': self.statistics['total_messages_consumed'],
                'total_anomalies_detected': self.statistics['total_anomalies_detected'],
                'processing_rate': (self.statistics['total_messages_consumed'] / uptime) if uptime else 0
            }
        }
    
    def send_custom_sensor_data(self, sensor_data: Dict[str, Any], 
                               production_line: str = "custom") -> bool:
        """Send custom sensor data through the stream."""
        if not self.is_running:
            logger.warning("Stream manager is not running")
            return False
        
        return self.producer.send_sensor_data(sensor_data, production_line)
    
    def get_active_windows(self) -> Dict[str, int]:
        """Get information about active processing windows."""
        if not self.consumer:
            return {}
        
        return self.consumer.get_statistics().get('active_windows', {})


# Example alert handlers
def console_alert_handler(anomaly: Dict[str, Any]):
    """Simple console alert handler."""
    print(f"🚨 ALERT: {anomaly['anomaly_type']} anomaly detected!")
    print(f"   Component: {anomaly['component_id']}")
    print(f"   Production Line: {anomaly['production_line']}")
    print(f"   Severity: {anomaly['severity']}")
    print(f"   Timestamp: {anomaly['timestamp']}")

def database_alert_handler(anomaly: Dict[str, Any]):
    """Database alert handler (placeholder)."""
    # This would store anomalies in a database
    logger.info(f"Storing anomaly in database: {anomaly['component_id']}")

def email_alert_handler(anomaly: Dict[str, Any]):
    """Email alert handler (placeholder)."""
    # This would send email alerts
    logger.info(f"Sending email alert for: {anomaly['component_id']}") 