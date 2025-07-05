import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import threading
from queue import Queue, Full
import random

# Try to import real Kafka, fall back to mock if not available
try:
    from kafka import KafkaProducer
    from kafka.errors import KafkaError, KafkaTimeoutError
    KAFKA_AVAILABLE = True
    logger = logging.getLogger(__name__)
except ImportError:
    # Use mock Kafka implementation
    from .mock_kafka import MockKafkaProducer as KafkaProducer
    from .mock_kafka import MockFuture
    KAFKA_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.info("Real Kafka not available, using mock implementation")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Alert handler functions
def console_alert_handler(anomaly: Dict[str, Any]):
    """Console alert handler for anomalies."""
    print(f"🚨 CONSOLE ALERT: {anomaly.get('anomaly_type', 'unknown')} anomaly detected!")
    print(f"   Component: {anomaly.get('component_id', 'unknown')}")
    print(f"   Production Line: {anomaly.get('production_line', 'unknown')}")
    print(f"   Severity: {anomaly.get('severity', 'unknown')}")
    print(f"   Timestamp: {anomaly.get('timestamp', 'unknown')}")

def database_alert_handler(anomaly: Dict[str, Any]):
    """Database alert handler for anomalies."""
    logger.info(f"Database alert: {anomaly.get('anomaly_type', 'unknown')} anomaly for "
                f"component {anomaly.get('component_id', 'unknown')}")

def email_alert_handler(anomaly: Dict[str, Any]):
    """Email alert handler for anomalies."""
    logger.info(f"Email alert: {anomaly.get('anomaly_type', 'unknown')} anomaly for "
                f"component {anomaly.get('component_id', 'unknown')}")

class SensorDataProducer:
    """Advanced Kafka producer for sensor data streaming with backpressure handling."""
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092', 
                 topic: str = 'sensor-data', 
                 max_queue_size: int = 1000,
                 batch_size: int = 100,
                 linger_ms: int = 100):
        """
        Initialize the sensor data producer.
        
        Args:
            bootstrap_servers: Kafka broker addresses
            topic: Kafka topic for sensor data
            max_queue_size: Maximum size of internal message queue
            batch_size: Number of messages to batch before sending
            linger_ms: Time to wait for more messages before sending batch
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.max_queue_size = max_queue_size
        self.batch_size = batch_size
        self.linger_ms = linger_ms
        
        # Internal message queue for backpressure handling
        self.message_queue = Queue(maxsize=max_queue_size)
        self.producer = None
        self.is_running = False
        self.producer_thread = None
        
        # Statistics
        self.messages_sent = 0
        self.messages_dropped = 0
        self.errors = 0
        
        self._initialize_producer()
    
    def _initialize_producer(self):
        """Initialize Kafka producer with error handling."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                batch_size=self.batch_size,
                linger_ms=self.linger_ms,
                retries=3,
                acks='all',  # Wait for all replicas
                compression_type='gzip',
                max_in_flight_requests_per_connection=1
            )
            logger.info(f"Kafka producer initialized successfully for topic: {self.topic}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            raise
    
    def start(self):
        """Start the producer thread."""
        if not self.is_running:
            self.is_running = True
            self.producer_thread = threading.Thread(target=self._producer_worker, daemon=True)
            self.producer_thread.start()
            logger.info("Sensor data producer started")
    
    def stop(self):
        """Stop the producer thread and close connections."""
        self.is_running = False
        if self.producer_thread:
            self.producer_thread.join(timeout=5)
        
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("Sensor data producer stopped")
    
    def _producer_worker(self):
        """Worker thread that processes messages from the queue."""
        batch = []
        last_send_time = time.time()
        
        while self.is_running:
            try:
                # Try to get message from queue with timeout
                try:
                    message = self.message_queue.get(timeout=1.0)
                    batch.append(message)
                except:
                    # No message available, check if we should send current batch
                    if batch and (time.time() - last_send_time) > (self.linger_ms / 1000.0):
                        self._send_batch(batch)
                        batch = []
                        last_send_time = time.time()
                    continue
                
                # Send batch if it's full or enough time has passed
                if len(batch) >= self.batch_size or (time.time() - last_send_time) > (self.linger_ms / 1000.0):
                    self._send_batch(batch)
                    batch = []
                    last_send_time = time.time()
                    
            except Exception as e:
                logger.error(f"Error in producer worker: {e}")
                self.errors += 1
                time.sleep(1)  # Back off on error
    
    def _send_batch(self, batch: list):
        """Send a batch of messages to Kafka."""
        if not batch:
            return
        
        try:
            for message in batch:
                future = self.producer.send(
                    self.topic,
                    value=message['data'],
                    key=message['key']
                )
                # Handle the future asynchronously
                future.add_callback(self._on_send_success)
                future.add_errback(self._on_send_error)
            
            self.producer.flush()
            self.messages_sent += len(batch)
            logger.debug(f"Sent batch of {len(batch)} messages")
            
        except Exception as e:
            logger.error(f"Error sending batch: {e}")
            self.errors += 1
            self.messages_dropped += len(batch)
    
    def _on_send_success(self, record_metadata):
        """Callback for successful message send."""
        logger.debug(f"Message sent successfully to {record_metadata.topic} "
                    f"partition {record_metadata.partition} "
                    f"offset {record_metadata.offset}")
    
    def _on_send_error(self, excp):
        """Callback for failed message send."""
        logger.error(f"Failed to send message: {excp}")
        self.errors += 1
    
    def send_sensor_data(self, sensor_data: Dict[str, Any], 
                        production_line: str = "default") -> bool:
        """
        Send sensor data to Kafka with backpressure handling.
        
        Args:
            sensor_data: Sensor data dictionary
            production_line: Production line identifier for partitioning
            
        Returns:
            bool: True if message was queued successfully, False if dropped
        """
        if not self.is_running:
            logger.warning("Producer is not running")
            return False
        
        # Add metadata to sensor data
        message_data = {
            **sensor_data,
            'timestamp': datetime.now().isoformat(),
            'producer_id': id(self),
            'sequence_number': self.messages_sent + self.messages_dropped
        }
        
        # Create message with key for partitioning
        message = {
            'data': message_data,
            'key': production_line
        }
        
        # Try to add to queue (handles backpressure)
        try:
            self.message_queue.put_nowait(message)
            return True
        except Full:
            # Queue is full, drop message
            self.messages_dropped += 1
            logger.warning(f"Message queue full, dropping message. "
                         f"Dropped: {self.messages_dropped}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get producer statistics."""
        return {
            'messages_sent': self.messages_sent,
            'messages_dropped': self.messages_dropped,
            'errors': self.errors,
            'queue_size': self.message_queue.qsize(),
            'queue_max_size': self.max_queue_size,
            'success_rate': (self.messages_sent / (self.messages_sent + self.messages_dropped)) 
                           if (self.messages_sent + self.messages_dropped) > 0 else 0
        }


class AdvancedSensorSimulator:
    """Advanced sensor data simulator with realistic patterns and anomalies."""
    
    def __init__(self, producer: SensorDataProducer):
        self.producer = producer
        self.is_running = False
        self.simulation_thread = None
        
        # Simulation parameters
        self.anomaly_probability = 0.05  # 5% chance of anomaly
        self.trend_duration = 300  # 5 minutes
        self.seasonal_period = 3600  # 1 hour
        
    def start_simulation(self, interval_seconds: float = 1.0):
        """Start continuous sensor data simulation."""
        if not self.is_running:
            self.is_running = True
            self.simulation_thread = threading.Thread(
                target=self._simulation_worker, 
                args=(interval_seconds,),
                daemon=True
            )
            self.simulation_thread.start()
            logger.info("Advanced sensor simulation started")
    
    def stop_simulation(self):
        """Stop the simulation."""
        self.is_running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=5)
        logger.info("Advanced sensor simulation stopped")
    
    def _simulation_worker(self, interval_seconds: float):
        """Worker thread for continuous sensor data generation."""
        start_time = time.time()
        
        while self.is_running:
            try:
                # Generate sensor data with realistic patterns
                sensor_data = self._generate_realistic_sensor_data(start_time)
                
                # Send to Kafka
                success = self.producer.send_sensor_data(
                    sensor_data, 
                    production_line=sensor_data['production_line']
                )
                
                if not success:
                    logger.warning("Failed to send sensor data due to backpressure")
                
                time.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in simulation worker: {e}")
                time.sleep(interval_seconds)
    
    def _generate_realistic_sensor_data(self, start_time: float) -> Dict[str, Any]:
        """Generate realistic sensor data with trends, seasonality, and anomalies."""
        current_time = time.time()
        elapsed_time = current_time - start_time
        
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
        is_anomaly = random.random() < self.anomaly_probability
        
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
            'temperature': round(temperature, 2),
            'humidity': round(humidity, 2),
            'sound': round(sound, 2),
            'production_line': random.choice(['blade_production', 'nacelle_assembly']),
            'component_id': f"comp_{random.randint(1000, 9999)}",
            'is_anomaly': is_anomaly,
            'anomaly_type': anomaly_type if is_anomaly else None,
            'sensor_id': f"sensor_{random.randint(1, 10)}",
            'batch_id': f"batch_{int(elapsed_time / 60)}"  # New batch every minute
        }


# Import numpy for mathematical operations
import numpy as np 