from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from model.pydantic import CreateSensorDataRequest, PredictionRequest, SensorData
from kafta import KaftaService
from config import KAFKA_TOPIC, COLLECTIONS
from db import database_handler
from utils.authentication import AuthHandler
from machine_learning import model, train_model, scaler
import json
import pandas as pd
from typing import List

sensor_data_router = APIRouter()
kafka_service = KaftaService()

@sensor_data_router.post("/ingest")
async def ingest_sensor_data(data: CreateSensorDataRequest, background_tasks: BackgroundTasks): 
    try:
        database_handler.insert_document(collection=COLLECTIONS.get('sensor'), document=dict(data))
        producer = kafka_service.get_producer()
        json_data = json.dumps(dict(data))
        producer.produce(KAFKA_TOPIC, value=json_data.encode('utf-8'))
        producer.flush()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kafka publish failed: {str(e)}")
    return {"message": "Sensor data sent to Kafka topic"}

@sensor_data_router.post("/predict")
async def predict_failure(request: PredictionRequest):
    sensor_data: List[SensorData] = database_handler.find_documents(collection=COLLECTIONS.get('sensor'), query={"equipment_id": request.equipment_id})
    if not sensor_data:
        raise HTTPException(status_code=400, detail="No sensor data available")
    latest_sensor_data = sensor_data[0]
    feature_names = [
            'device', 'metric1', 'metric2',
            'metric3', 'metric4', 'metric5',
            'metric6', 'metric7', 'metric8', 'metric9'
        ]
    input_data = [[latest_sensor_data['metric1'], latest_sensor_data['metric2'], latest_sensor_data['metric3'], latest_sensor_data['metric4'], latest_sensor_data['metric5'], latest_sensor_data['metric6'], latest_sensor_data['metric7'], latest_sensor_data['metric8'], latest_sensor_data['metric9']]]

    input_df = pd.DataFrame(input_data, columns=feature_names)

    input_scaled = scaler.transform(input_df)
    prediction = model.predict(input_scaled)
    if prediction[0] == 1:
        return {"prediction": "Failure predicted"}
    else:
        return {"prediction": "No failure predicted"}