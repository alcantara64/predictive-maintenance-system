from typing import List
from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
import asyncio
import json
# from bson import ObjectId
from contextlib import asynccontextmanager
from config import COLLECTIONS, DATABASE_NAME, KAFKA_TOPIC, MONGO_URI
from db import database_handler
from model.pydantic import CreateEquipmentRequest, CreateSensorDataRequest, MaintenanceRequest, PredictionRequest, SensorData, UserLogin, UserRegistration
from utils.authentication import AuthHandler
from kafta import KaftaService
from machine_learning import model, train_model, scaler
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd




# Simulated sensor data storage
sensor_data = []
maintenance_schedule = []

origins = [
    "http://localhost:3000",  # Example frontend URL
    "https://your-frontend.com",  # Your deployed frontend URL
    "*",  # Allow all (use with caution)
]

# Add CORS middleware


auth_handler = AuthHandler()
kafka_service = KaftaService()



#database intialiazation
@asynccontextmanager
async def lifespan(app: FastAPI):
    await database_handler.connect()
    yield
    await database_handler.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,  
    allow_methods=["*"], 
    allow_headers=["*"],  
)

# User registration endpoint
@app.post("/register")
def register(user: UserRegistration):
    # Check if the user already exists
    existing_user = database_handler.find_documents(collection=COLLECTIONS.get('user'),query={"email":user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hash the password and insert the user
    hashed_password = auth_handler.hash_password(user.password)
    new_user = {**dict(user), "password": hashed_password}
    database_handler.insert_document(collection=COLLECTIONS.get('user'),document=new_user)
    return {"message": "User registered successfully"}

@app.post("/token")
def login(form_data: UserLogin):
    # Find the user in the database
    user = database_handler.find_one_document(collection=COLLECTIONS.get('user'),query={"email":form_data.username})
    if not user or not auth_handler.verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Generate a JWT token
    access_token = auth_handler.create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# calculate dashboard data
@app.get("/dashboard")
async def get_dashboard():
    user_count = database_handler.get_document_count(collection=COLLECTIONS.get('user'),query={})
    equipment_count = database_handler.get_document_count(collection=COLLECTIONS.get('equipment'),query={})
    maintenance_count = database_handler.get_document_count(collection=COLLECTIONS.get('maintenance'),query={})
    
    return {"equipment":equipment_count, "user": user_count, "maintenance_request": maintenance_count }
    
@app.get("/users")
async def get_users():
    users = database_handler.find_documents(collection=COLLECTIONS.get('user'))
    return users 

# Simulated notification system
async def send_notification(message: str):
    print(f"Notification sent: {message}")
    await asyncio.sleep(1)  # Simulate async operation

# Data ingestion endpoint
@app.post("/ingest-sensor-data")
async def ingest_sensor_data(data: CreateSensorDataRequest, background_tasks: BackgroundTasks):
    # Send data to Kafka topic
    # producer = kafka_producer()
    # producer.produce(KAFKA_TOPIC, key=data.equipment_id, value=data.json())
    # producer.flush()
    # background_tasks.add_task(process_kafka_messages)
    database_handler.insert_document(collection=COLLECTIONS.get('sensor'), document=dict(data))
    return {"message": "Sensor data sent to Kafka topic"}

# Process Kafka messages
def process_kafka_messages():
    consumer = kafka_service.consumer()
    consumer.subscribe([KAFKA_TOPIC])
    
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == kafka_service.error()._PARTITION_EOF:
                continue
            else:
                print(f"Kafka error: {msg.error()}")
                break
        
        # Decode the message
        data = json.loads(msg.value())
        print(f" ingested data {data}")
        # MongoDBHandler(connection_string=MONGO_URI,database_name=DATABASE_NAME).insert_document(data)
        sensor_data.append(data)
        print(data)
        print(f"Processed sensor data: {data}")

# Predict equipment failure
@app.post("/predict-failure")
async def predict_failure(request: PredictionRequest):    
    #get the latest sensor data
    sensor_data:List[SensorData] = database_handler.find_documents(collection=COLLECTIONS.get('sensor'), query={})
    latest_sensor_data = sensor_data[0]
    # Prepare input data
    feature_names = [
    'Type', 'Air temperature [K]', 'Process temperature [K]', 
    'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]', 
    'TWF', 'HDF', 'PWF', 'OSF', 'RNF'
     ]
    input_data = [[latest_sensor_data['air_temperature'], latest_sensor_data['air_temperature'], latest_sensor_data['process_temperature'], latest_sensor_data['rotational_speed'], latest_sensor_data['torque'], latest_sensor_data['tool_wear'], latest_sensor_data['twf'],latest_sensor_data['hdf'], latest_sensor_data['pwf'],latest_sensor_data['osf'], latest_sensor_data['rnf']]]
    
    input_df = pd.DataFrame(input_data, columns=feature_names)
     
    input_scaled = scaler.transform(input_df)
    prediction = model.predict(input_scaled)
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

@app.post("/equipment")
async def create_equipment(equipment: CreateEquipmentRequest):
    equipment = database_handler.insert_document(collection=COLLECTIONS.get('equipment'), document=dict(equipment))
    if equipment == None:
        raise HTTPException(status_code=500, detail="Could not create equipment")
    return {"message": 'Equipment created successfully'}

@app.get("/equipments")
async def get_equipments():
    equipments = database_handler.find_documents(collection=COLLECTIONS.get('equipment'))
    if equipments == None:
        raise HTTPException(status_code=500, detail="Could not fetch equipments")
    return {"data": equipments}
    
# Get maintenance schedule
@app.get("/maintenance-schedule")
async def get_maintenance_schedule():
    return {"maintenance_schedule": maintenance_schedule}

# Simulate real-time monitoring
@app.get("/monitor-equipment")
async def monitor_equipment(current_user: dict = Depends(auth_handler.get_current_user)):
    if not sensor_data:
        raise HTTPException(status_code=400, detail="No sensor data available")
    
    latest_data = sensor_data[-1]
    return {"latest_sensor_data": latest_data}

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)