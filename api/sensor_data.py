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
    database_handler.insert_document(collection=COLLECTIONS.get('sensor'), document=dict(data))
    return {"message": "Sensor data sent to Kafka topic"}

@sensor_data_router.post("/predict")
async def predict_failure(request: PredictionRequest):
    sensor_data: List[SensorData] = database_handler.find_documents(collection=COLLECTIONS.get('sensor'), query={})
    if not sensor_data:
        raise HTTPException(status_code=400, detail="No sensor data available")
    latest_sensor_data = sensor_data[0]
    feature_names = [
        'Type', 'Air temperature [K]', 'Process temperature [K]',
        'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]',
        'TWF', 'HDF', 'PWF', 'OSF', 'RNF'
    ]
    input_data = [[latest_sensor_data['air_temperature'], latest_sensor_data['air_temperature'], latest_sensor_data['process_temperature'], latest_sensor_data['rotational_speed'], latest_sensor_data['torque'], latest_sensor_data['tool_wear'], latest_sensor_data['twf'], latest_sensor_data['hdf'], latest_sensor_data['pwf'], latest_sensor_data['osf'], latest_sensor_data['rnf']]]

    input_df = pd.DataFrame(input_data, columns=feature_names)

    input_scaled = scaler.transform(input_df)
    prediction = model.predict(input_scaled)
    if prediction[0] == 1:
        return {"prediction": "Failure predicted"}
    else:
        return {"prediction": "No failure predicted"}