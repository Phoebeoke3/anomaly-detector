# Streaming Processing Architecture

## Apache Flink Processing Engine

```ascii
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|  Kafka           |     |  Flink           |     |  Storage         |
|  Source          +---->+  Processing      +---->+  Sinks           |
|                  |     |  Engine          |     |                  |
+------------------+     +------------------+     +------------------+
                                                         |
                                                         v
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|  State           |<----|  Window          |<----|  Processing      |
|  Management      |     |  Operations      |     |  Logic           |
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
```

## Flink Processing Components

### 1. Data Sources
- **Kafka Source**
  ```python
  from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
  
  kafka_source = KafkaSource.builder() \
      .set_bootstrap_servers("kafka:9092") \
      .set_topics("sensor-data") \
      .set_starting_offsets(KafkaOffsetsInitializer.latest()) \
      .set_value_only_deserializer(SimpleStringSchema()) \
      .build()
  ```

### 2. Processing Operations
- **Window Operations**
  ```python
  from pyflink.common.time import Time
  from pyflink.datastream.window import TumblingEventTimeWindows
  
  # 5-minute tumbling windows
  windowed_stream = stream \
      .key_by(lambda x: x['sensor_id']) \
      .window(TumblingEventTimeWindows.of(Time.minutes(5)))
  ```

- **State Management**
  ```python
  from pyflink.common.state import ValueStateDescriptor
  
  class AnomalyDetector(KeyedProcessFunction):
      def __init__(self):
          self.state = None
          
      def open(self, parameters):
          state_descriptor = ValueStateDescriptor("anomaly-state", Types.FLOAT())
          self.state = self.get_runtime_context().get_state(state_descriptor)
  ```

### 3. Processing Logic
- **Anomaly Detection**
  ```python
  class AnomalyDetectionProcess(KeyedProcessFunction):
      def process_element(self, value, ctx, out):
          # Calculate anomaly score
          score = self.calculate_anomaly_score(value)
          
          # Update state
          self.state.update(score)
          
          # Emit result
          out.collect({
              'sensor_id': value['sensor_id'],
              'timestamp': value['timestamp'],
              'anomaly_score': score
          })
  ```

### 4. Data Sinks
- **Cassandra Sink**
  ```python
  from pyflink.connector.cassandra import CassandraSink
  
  cassandra_sink = CassandraSink.builder() \
      .set_host("cassandra") \
      .set_port(9042) \
      .set_keyspace("anomaly_detection") \
      .set_table("anomaly_scores") \
      .build()
  ```

## Processing Pipeline

1. **Data Ingestion**
   ```python
   # Create Flink environment
   env = StreamExecutionEnvironment.get_execution_environment()
   
   # Add Kafka source
   stream = env.add_source(kafka_source)
   ```

2. **Data Processing**
   ```python
   # Process stream
   processed_stream = stream \
       .map(validate_data) \
       .key_by(lambda x: x['sensor_id']) \
       .window(TumblingEventTimeWindows.of(Time.minutes(5))) \
       .process(AnomalyDetectionProcess())
   ```

3. **Data Output**
   ```python
   # Add sink
   processed_stream.add_sink(cassandra_sink)
   
   # Execute job
   env.execute("Anomaly Detection Job")
   ```

## Key Features

1. **Windowing**
   - Tumbling windows (5-minute intervals)
   - Sliding windows (overlapping intervals)
   - Session windows (activity-based)

2. **State Management**
   - Keyed state for per-sensor tracking
   - Operator state for global statistics
   - Checkpointing for fault tolerance

3. **Processing Guarantees**
   - Exactly-once processing
   - Event time processing
   - Watermark handling

4. **Performance Optimizations**
   - Parallel processing
   - State backend optimization
   - Network buffer tuning

## Monitoring & Metrics

1. **Flink Metrics**
   - Processing latency
   - Throughput
   - State size
   - Checkpoint duration

2. **Custom Metrics**
   - Anomaly detection accuracy
   - Processing time per window
   - Error rates
   - Resource utilization

## Error Handling

1. **Fault Tolerance**
   - Checkpointing
   - State recovery
   - Job restart

2. **Error Recovery**
   - Dead letter queues
   - Retry mechanisms
   - Error logging

## Configuration

1. **Flink Configuration**
   ```yaml
   jobmanager:
     memory:
       process:
         size: 2048m
   taskmanager:
     memory:
       process:
         size: 4096m
     number-of-task-slots: 4
   ```

2. **Kafka Configuration**
   ```yaml
   kafka:
     bootstrap.servers: kafka:9092
     group.id: anomaly-detection
     auto.offset.reset: latest
   ```

3. **Cassandra Configuration**
   ```yaml
   cassandra:
     contact-points: cassandra
     port: 9042
     keyspace: anomaly_detection
     consistency-level: LOCAL_QUORUM
   ```

## Cloud-Native Architecture

.
├── cloud/
│   ├── terraform/            # Infrastructure as Code (optional)
│   └── deployment/           # Dockerfiles, cloudbuild.yaml, etc.
├── src/
│   ├── data/
│   │   └── generator.py      # Sensor data generator (can run as Lambda or container)
│   ├── model/
│   │   └── train.py          # Model training (can run as batch job or notebook)
│   ├── api/
│   │   └── app.py            # REST API (Flask/FastAPI, containerized for cloud)
│   └── dashboard/
│       └── app.py            # Streamlit/Dash dashboard (containerized)
├── requirements.txt
└── README.md 

## Conceptual Docker Compose Architecture

**Services:**
- **data-generator**: Simulates sensor data and sends it to the API.
- **model-api**: Serves the trained anomaly detection model via a REST API (Flask/FastAPI).
- **dashboard**: Visualizes predictions and system status (Streamlit or Dash).
- **db**: Stores data (SQLite or Postgres for more realism).

## Directory Structure

```
anomaly-detection/
├── docker-compose.yml
├── src/
│   ├── data/
│   │   └── generator.py
│   ├── model/
│   │   └── train.py
│   ├── api/
│   │   └── app.py
│   └── dashboard/
│       └── app.py
├── requirements.txt
└── README.md
```

## Example `docker-compose.yml`

```yaml
version: '3.8'

services:
  model-api:
    build: ./src/api
    ports:
      - "8080:8080"
    volumes:
      - ./src/model/model.joblib:/app/model.joblib

  data-generator:
    build: ./src/data
    depends_on:
      - model-api

  dashboard:
    build: ./src/dashboard
    ports:
      - "8501:8501"
    depends_on:
      - model-api

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: anomaly
      POSTGRES_PASSWORD: anomaly
      POSTGRES_DB: anomalydb
    ports:
      - "5432:5432"
```

## Example Dockerfiles

**src/api/Dockerfile**
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY ../../requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
```

**src/data/Dockerfile**
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY ../../requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "generator.py"]
```

**src/dashboard/Dockerfile**
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY ../../requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Example Service Code

**src/data/generator.py**
```python
import requests
import random
import time

API_URL = "http://model-api:8080/predict"

def generate_sensor_data():
    return {
        "temperature": random.uniform(20, 30),
        "humidity": random.uniform(40, 60),
        "sound_level": random.uniform(50, 70)
    }

while True:
    data = generate_sensor_data()
    try:
        r = requests.post(API_URL, json=data)
        print("Sent:", data, "Response:", r.json())
    except Exception as e:
        print("Error:", e)
    time.sleep(1)
```

**src/api/app.py**
```python
from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)
model = joblib.load('model.joblib')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    X = np.array([[data['temperature'], data['humidity'], data['sound_level']]])
    score = float(model.decision_function(X)[0])
    return jsonify({'anomaly_score': score})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

**src/dashboard/app.py** (Streamlit example)
```python
import streamlit as st
import requests

st.title("Anomaly Detection Dashboard")

if st.button("Get Prediction"):
    data = {"temperature": 25, "humidity": 50, "sound_level": 60}
    response = requests.post("http://model-api:8080/predict", json=data)
    st.write(response.json())
```

## How to Run

1. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

2. **Access the dashboard:**
   - Go to [http://localhost:8501](http://localhost:8501)

3. **API is available at:**
   - [http://localhost:8080/predict](http://localhost:8080/predict)

## Open Data Source
- Use the SECOM dataset from Kaggle for model training.
- Simulate streaming by sending rows at intervals from the data-generator service.

## Visual Overview

```
[data-generator] ---> [model-api] ---> [dashboard]
         |                |                |
         +------------> [db] <-------------+
```

## Cloud-Ready
- You can deploy each service to AWS ECS, Azure Container Apps, or GCP Cloud Run with minimal changes.
- You can swap the database for a managed cloud database.

## Ready-to-Use Codebase
If you want a ready-to-use codebase or a zipped starter template, let me know!