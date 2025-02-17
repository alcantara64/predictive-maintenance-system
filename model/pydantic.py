from pydantic import BaseModel
from datetime import datetime
# Pydantic models for request/response validation
class UserRegistration(BaseModel):
    username: str
    password: str
    email: str
    role: str
    first_name:str
    last_name:str
    last_login:str
    

class UserLogin(BaseModel):
    username: str
    password: str
    last_login: None | str
    
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