from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np
import asyncio
from confluent_kafka import Producer, Consumer, KafkaError
import json
import joblib

app = FastAPI()

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "sensor_data_topic"

# Simulated sensor data storage
sensor_data = []
maintenance_schedule = []

# loading the trained model
model = joblib.load('best_predictive_maintenance_model.pkl')

# Pydantic models for request/response validation
class SensorData(BaseModel):
    equipment_id: str
    temperature: float
    vibration: float
    pressure: float
    timestamp: datetime

class MaintenanceRequest(BaseModel):
    equipment_id: str
    maintenance_type: str
    scheduled_time: datetime

class PredictionRequest(BaseModel):
    equipment_id: str
    sensor_data: SensorData

# Kafka Producer
def kafka_producer():
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'client.id': 'fastapi-producer'
    }
    return Producer(conf)

# Kafka Consumer
def kafka_consumer():
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'fastapi-consumer',
        'auto.offset.reset': 'earliest'
    }
    return Consumer(conf)

# Simulated notification system
async def send_notification(message: str):
    print(f"Notification sent: {message}")
    await asyncio.sleep(1)  # Simulate async operation

# Data ingestion endpoint
@app.post("/ingest-sensor-data")
async def ingest_sensor_data(data: SensorData, background_tasks: BackgroundTasks):
    # Send data to Kafka topic
    producer = kafka_producer()
    producer.produce(KAFKA_TOPIC, key=data.equipment_id, value=data.json())
    producer.flush()
    background_tasks.add_task(process_kafka_messages)
    return {"message": "Sensor data sent to Kafka topic"}

# Process Kafka messages
def process_kafka_messages():
    consumer = kafka_consumer()
    consumer.subscribe([KAFKA_TOPIC])
    
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Kafka error: {msg.error()}")
                break
        
        # Decode the message
        data = json.loads(msg.value())
        sensor_data.append(data)
        print(f"Processed sensor data: {data}")

# Data processing and cleaning
def process_data():
    if not sensor_data:
        raise HTTPException(status_code=400, detail="No sensor data available")
    
    df = pd.DataFrame(sensor_data)
    df = df.dropna()  # Remove missing values
    dd = df.drop(['UDI', 'equipment_id'], axis=1)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Train predictive model
def train_model():
    global model
    df = process_data()
    
    # Simulate failure labels (for demonstration purposes)
    df['failure'] = np.random.randint(0, 2, size=len(df))
    
    # Features and target
    X = df[['temperature', 'vibration', 'pressure']]
    y = df['failure']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model trained with accuracy: {accuracy}")

# Predict equipment failure
@app.post("/predict-failure")
async def predict_failure(request: PredictionRequest):
    if not model:
        train_model()
    
    # Prepare input data
    input_data = [[request.sensor_data.temperature, request.sensor_data.vibration, request.sensor_data.pressure]]
    prediction = model.predict(input_data)
    
    if prediction[0] == 1:
        message = f"Failure predicted for equipment {request.equipment_id}. Schedule maintenance immediately."
        await send_notification(message)
        return {"prediction": "Failure predicted", "message": message}
    else:
        return {"prediction": "No failure predicted"}

# Schedule maintenance
@app.post("/schedule-maintenance")
async def schedule_maintenance(request: MaintenanceRequest):
    maintenance_schedule.append(request.dict())
    message = f"Maintenance scheduled for equipment {request.equipment_id} at {request.scheduled_time}."
    await send_notification(message)
    return {"message": "Maintenance scheduled successfully"}

# Get maintenance schedule
@app.get("/maintenance-schedule")
async def get_maintenance_schedule():
    return {"maintenance_schedule": maintenance_schedule}

# Simulate real-time monitoring
@app.get("/monitor-equipment")
async def monitor_equipment():
    if not sensor_data:
        raise HTTPException(status_code=400, detail="No sensor data available")
    
    latest_data = sensor_data[-1]
    return {"latest_sensor_data": latest_data}

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)