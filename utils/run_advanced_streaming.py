#!/usr/bin/env python3
"""
Advanced Stream Processing Runner for IoT Anomaly Detection

This script demonstrates the advanced stream processing capabilities including:
- Kafka producer/consumer for robust message handling
- Time-based and count-based windowing
- Real-time anomaly detection with statistical analysis
- Backpressure handling and error recovery
- Comprehensive monitoring and alerting
"""

import sys
import os
import time
import signal
import argparse
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from streaming import StreamManager, StreamConfig, StreamProcessingMode, WindowType
from streaming.kafka_producer import console_alert_handler, database_alert_handler, email_alert_handler

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("\n🛑 Received shutdown signal. Stopping stream processing...")
    if hasattr(signal_handler, 'stream_manager'):
        signal_handler.stream_manager.stop()
    sys.exit(0)

def main():
    """Main function to run the advanced stream processing system."""
    parser = argparse.ArgumentParser(description='Advanced Stream Processing for IoT Anomaly Detection')
    parser.add_argument('--kafka-servers', default='localhost:9092', 
                       help='Kafka bootstrap servers (default: localhost:9092)')
    parser.add_argument('--topic', default='sensor-data', 
                       help='Kafka topic for sensor data (default: sensor-data)')
    parser.add_argument('--window-type', choices=['time', 'count'], default='time',
                       help='Window type for stream processing (default: time)')
    parser.add_argument('--window-size', type=int, default=60,
                       help='Window size in seconds (time) or count (count) (default: 60)')
    parser.add_argument('--simulation-interval', type=float, default=1.0,
                       help='Sensor data simulation interval in seconds (default: 1.0)')
    parser.add_argument('--anomaly-probability', type=float, default=0.05,
                       help='Probability of anomaly injection (default: 0.05)')
    parser.add_argument('--mode', choices=['real_time', 'batch', 'hybrid'], default='real_time',
                       help='Processing mode (default: real_time)')
    
    args = parser.parse_args()
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 Starting Advanced Stream Processing System")
    print("=" * 60)
    print(f"Kafka Servers: {args.kafka_servers}")
    print(f"Topic: {args.topic}")
    print(f"Window Type: {args.window_type}")
    print(f"Window Size: {args.window_size}")
    print(f"Simulation Interval: {args.simulation_interval}s")
    print(f"Anomaly Probability: {args.anomaly_probability}")
    print(f"Processing Mode: {args.mode}")
    print("=" * 60)
    
    try:
        # Create stream configuration
        config = StreamConfig(
            kafka_bootstrap_servers=args.kafka_servers,
            sensor_data_topic=args.topic,
            window_type=WindowType.TIME if args.window_type == 'time' else WindowType.COUNT,
            window_size=args.window_size,
            processing_mode=StreamProcessingMode(args.mode),
            simulation_interval=args.simulation_interval,
            anomaly_probability=args.anomaly_probability
        )
        
        # Create and configure stream manager
        stream_manager = StreamManager(config)
        
        # Add alert handlers
        stream_manager.add_alert_handler(console_alert_handler)
        stream_manager.add_alert_handler(database_alert_handler)
        stream_manager.add_alert_handler(email_alert_handler)
        
        # Store reference for signal handler
        signal_handler.stream_manager = stream_manager
        
        # Start the stream processing system
        stream_manager.start()
        
        print("✅ Stream processing system started successfully!")
        print("📊 Monitoring system statistics...")
        print("Press Ctrl+C to stop")
        
        # Monitor and display statistics
        last_stats_time = time.time()
        while True:
            time.sleep(10)  # Update every 10 seconds
            
            # Get and display statistics
            stats = stream_manager.get_system_statistics()
            
            # Only display if there's new activity
            if stats['summary']['total_messages_consumed'] > 0:
                print(f"\n📈 System Statistics ({datetime.now().strftime('%H:%M:%S')})")
                print("-" * 40)
                print(f"Status: {stats['system']['status']} | Health: {stats['system']['health']}")
                print(f"Messages Produced: {stats['summary']['total_messages_produced']}")
                print(f"Messages Consumed: {stats['summary']['total_messages_consumed']}")
                print(f"Anomalies Detected: {stats['summary']['total_anomalies_detected']}")
                print(f"Processing Rate: {stats['summary']['processing_rate']:.2f} msg/s")
                
                # Display active windows
                active_windows = stream_manager.get_active_windows()
                if active_windows:
                    print(f"Active Windows: {active_windows}")
                
                # Display producer/consumer stats
                if stats['producer']:
                    print(f"Producer Success Rate: {stats['producer'].get('success_rate', 0):.2%}")
                    print(f"Producer Errors: {stats['producer'].get('errors', 0)}")
                
                if stats['consumer']:
                    print(f"Consumer Latency: {stats['consumer'].get('average_processing_latency', 0):.3f}s")
                
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