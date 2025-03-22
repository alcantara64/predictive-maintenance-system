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
    last_login:datetime | None 
    

class UserLogin(BaseModel):
    username: str
    password: str
    
class SensorData(BaseModel):
    equipment_id: str
    type: str
    air_temperature:float
    process_temperature:float
    rotational_speed:int
    torque:float
    tool_wear:int
    machine_failure:int
    twf:int
    hdf:int
    pwf:int
    osf:int
    rnf:int


class MaintenanceRequest(BaseModel):
    equipment_id: str
    maintenance_type: str
    scheduled_time: datetime

class PredictionRequest(BaseModel):
    equipment_id: str
    
class CreateSensorDataRequest(BaseModel):
    equipment_id: str
    type: str
    air_temperature:float
    process_temperature:float
    rotational_speed:int
    torque:float
    tool_wear:int
    machine_failure:int
    twf:int
    hdf:int
    pwf:int
    osf:int
    rnf:int

class CreateEquipmentRequest(BaseModel):
     
    type: str
    name:str
    manufacturer:str
    model_number: str
    serial_number: str
    status:bool
    location:str
    installation_date: datetime
    purchase_date: datetime
    cost:int
    date: datetime
    last_maintenance_date: datetime

    
    