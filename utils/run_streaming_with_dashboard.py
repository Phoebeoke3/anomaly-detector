#!/usr/bin/env python3
"""
Stream Processing with Dashboard Integration

This script starts the stream processing system and integrates it with the dashboard,
allowing you to see windowing and anomaly detection results in real-time.
"""

import sys
import os
import time
import signal
import argparse
import threading

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("\n🛑 Received shutdown signal. Stopping stream processing...")
    if hasattr(signal_handler, 'stream_manager'):
        signal_handler.stream_manager.stop()
    if hasattr(signal_handler, 'stream_integration'):
        signal_handler.stream_integration.stop()
    sys.exit(0)

def main():
    """Main function to run stream processing with dashboard integration."""
    parser = argparse.ArgumentParser(description='Stream Processing with Dashboard Integration')
    parser.add_argument('--window-type', choices=['time', 'count'], default='time',
                       help='Window type for stream processing (default: time)')
    parser.add_argument('--window-size', type=int, default=10,
                       help='Window size in seconds (time) or count (count) (default: 10)')
    parser.add_argument('--simulation-interval', type=float, default=1.0,
                       help='Sensor data simulation interval in seconds (default: 1.0)')
    parser.add_argument('--anomaly-probability', type=float, default=0.2,
                       help='Probability of anomaly injection (default: 0.2)')
    
    args = parser.parse_args()
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 Starting Stream Processing with Dashboard Integration")
    print("=" * 70)
    print(f"Window Type: {args.window_type}")
    print(f"Window Size: {args.window_size}")
    print(f"Simulation Interval: {args.simulation_interval}s")
    print(f"Anomaly Probability: {args.anomaly_probability}")
    print("=" * 70)
    
    try:
        # Initialize dashboard integration
        from src.streaming.dashboard_integration import stream_integration
        stream_integration.start()
        signal_handler.stream_integration = stream_integration
        
        print("✅ Dashboard integration started")
        
        # Import and start stream processing
        from utils.run_simple_streaming import SimpleStreamManager
        
        # Create stream manager
        stream_manager = SimpleStreamManager(
            window_size=args.window_size,
            window_type=args.window_type,
            simulation_interval=args.simulation_interval,
            anomaly_probability=args.anomaly_probability
        )
        
        # Store reference for signal handler
        signal_handler.stream_manager = stream_manager
        
        # Start the stream processing system
        stream_manager.start()
        
        print("✅ Stream processing system started successfully!")
        print("📊 Stream processing data will be available in your dashboard")
        print("🌐 Access your dashboard at: http://localhost:5001")
        print("📈 Check the dashboard for stream processing results")
        print("Press Ctrl+C to stop")
        
        # Monitor and display statistics
        last_stats_time = time.time()
        while True:
            time.sleep(10)  # Update every 10 seconds
            
            # Get and display statistics
            stats = stream_manager.get_statistics()
            
            # Only display if there's new activity
            if stats['processor']['windows_processed'] > 0:
                print(f"\n📈 Stream Processing Statistics ({time.strftime('%H:%M:%S')})")
                print("-" * 50)
                print(f"Status: {stats['summary']['total_messages_processed'] > 0 and 'running' or 'starting'}")
                print(f"Messages Sent: {stats['summary']['total_messages_sent']}")
                print(f"Messages Processed: {stats['summary']['total_messages_processed']}")
                print(f"Windows Processed: {stats['processor']['windows_processed']}")
                print(f"Anomalies Detected: {stats['summary']['total_anomalies_detected']}")
                print(f"Processing Latency: {stats['processor']['average_processing_latency']:.3f}s")
                
                # Display active windows
                active_windows = stats['processor']['active_windows']
                if active_windows:
                    print(f"Active Windows: {active_windows}")
                
                print("-" * 50)
                print("💡 Check your dashboard for detailed stream processing results!")
    
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal")
    except Exception as e:
        print(f"❌ Error running stream processing system: {e}")
        return 1
    finally:
        # Cleanup
        if 'stream_manager' in locals():
            stream_manager.stop()
        if 'stream_integration' in locals():
            stream_integration.stop()
        print("👋 Stream processing system stopped")

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 