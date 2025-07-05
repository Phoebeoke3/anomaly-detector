"""
Mock Kafka Implementation for Development and Testing

This module provides a mock implementation of Kafka producer and consumer
that works without requiring a real Kafka server. Perfect for development,
testing, and demonstrations.
"""

import json
import time
import threading
import queue
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MockMessage:
    """Mock Kafka message."""
    topic: str
    key: Optional[str]
    value: Dict[str, Any]
    timestamp: datetime
    partition: int = 0
    offset: int = 0

class MockKafkaProducer:
    """Mock Kafka producer for development and testing."""
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092', **kwargs):
        """Initialize mock producer."""
        self.bootstrap_servers = bootstrap_servers
        self.is_closed = False
        self.messages_sent = 0
        self.errors = 0
        
        # Connect to mock broker
        MockKafkaBroker.get_instance().register_producer(self)
        logger.info(f"Mock Kafka producer initialized for {bootstrap_servers}")
    
    def send(self, topic: str, value: Dict[str, Any], key: Optional[str] = None, **kwargs):
        """Send message to mock topic."""
        if self.is_closed:
            raise RuntimeError("Producer is closed")
        
        try:
            # Create mock message
            message = MockMessage(
                topic=topic,
                key=key,
                value=value,
                timestamp=datetime.now()
            )
            
            # Send to mock broker
            MockKafkaBroker.get_instance().publish_message(message)
            self.messages_sent += 1
            
            # Create mock future
            future = MockFuture(message)
            return future
            
        except Exception as e:
            self.errors += 1
            logger.error(f"Error sending message: {e}")
            raise
    
    def flush(self):
        """Flush any pending messages."""
        logger.debug("Mock producer flush called")
    
    def close(self):
        """Close the producer."""
        self.is_closed = True
        MockKafkaBroker.get_instance().unregister_producer(self)
        logger.info("Mock Kafka producer closed")

class MockKafkaConsumer:
    """Mock Kafka consumer for development and testing."""
    
    def __init__(self, topic: str, bootstrap_servers: str = 'localhost:9092', 
                 group_id: str = 'default-group', **kwargs):
        """Initialize mock consumer."""
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.is_closed = False
        self.messages_consumed = 0
        
        # Connect to mock broker
        MockKafkaBroker.get_instance().register_consumer(self, topic)
        logger.info(f"Mock Kafka consumer initialized for topic: {topic}")
    
    def poll(self, timeout_ms: int = 1000):
        """Poll for messages from mock topic."""
        if self.is_closed:
            return {}
        
        try:
            # Get messages from mock broker
            messages = MockKafkaBroker.get_instance().get_messages(self.topic, timeout_ms)
            
            if messages:
                self.messages_consumed += len(messages)
                # Return in Kafka format
                return {f"mock-partition-{self.topic}": messages}
            
            return {}
            
        except Exception as e:
            logger.error(f"Error polling messages: {e}")
            return {}
    
    def close(self):
        """Close the consumer."""
        self.is_closed = True
        MockKafkaBroker.get_instance().unregister_consumer(self)
        logger.info("Mock Kafka consumer closed")

class MockFuture:
    """Mock future for async operations."""
    
    def __init__(self, message: MockMessage):
        self.message = message
        self._callbacks = []
        self._errbacks = []
        self._completed = False
        self._result = None
        self._error = None
    
    def add_callback(self, callback: Callable):
        """Add success callback."""
        self._callbacks.append(callback)
        if self._completed and not self._error:
            callback(self.message)
    
    def add_errback(self, errback: Callable):
        """Add error callback."""
        self._errbacks.append(errback)
        if self._completed and self._error:
            errback(self._error)

class MockKafkaBroker:
    """Mock Kafka broker that manages topics and message routing."""
    
    _instance = None
    
    def __init__(self):
        self.topics = defaultdict(list)  # topic -> list of messages
        self.consumers = defaultdict(list)  # topic -> list of consumers
        self.producers = []
        self.message_counter = 0
        self._lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register_producer(self, producer):
        """Register a producer."""
        with self._lock:
            self.producers.append(producer)
    
    def unregister_producer(self, producer):
        """Unregister a producer."""
        with self._lock:
            if producer in self.producers:
                self.producers.remove(producer)
    
    def register_consumer(self, consumer, topic: str):
        """Register a consumer for a topic."""
        with self._lock:
            self.consumers[topic].append(consumer)
    
    def unregister_consumer(self, consumer):
        """Unregister a consumer."""
        with self._lock:
            for topic_consumers in self.consumers.values():
                if consumer in topic_consumers:
                    topic_consumers.remove(consumer)
    
    def publish_message(self, message: MockMessage):
        """Publish a message to a topic."""
        with self._lock:
            # Add message to topic
            self.topics[message.topic].append(message)
            self.message_counter += 1
            
            # Simulate some processing delay
            time.sleep(0.001)
            
            logger.debug(f"Published message to topic {message.topic}: {message.value.get('component_id', 'unknown')}")
    
    def get_messages(self, topic: str, timeout_ms: int) -> List[MockMessage]:
        """Get messages for a topic."""
        with self._lock:
            if topic in self.topics and self.topics[topic]:
                # Return all available messages
                messages = self.topics[topic].copy()
                self.topics[topic].clear()  # Remove consumed messages
                return messages
            return []
    
    def get_topic_stats(self) -> Dict[str, Any]:
        """Get statistics about topics."""
        with self._lock:
            return {
                'total_messages_published': self.message_counter,
                'topics': {topic: len(messages) for topic, messages in self.topics.items()},
                'active_consumers': sum(len(consumers) for consumers in self.consumers.values()),
                'active_producers': len(self.producers)
            }


# Mock kafka module for import compatibility
class MockKafka:
    """Mock kafka module that provides the same interface as kafka-python."""
    
    @staticmethod
    def KafkaProducer(**kwargs):
        return MockKafkaProducer(**kwargs)
    
    @staticmethod
    def KafkaConsumer(**kwargs):
        return MockKafkaConsumer(**kwargs)

# Create mock kafka module
kafka = MockKafka() 