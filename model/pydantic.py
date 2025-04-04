from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
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
    device: str
    metric1:int
    metric2:int
    metric3:int
    metric4:int
    metric5:int
    metric6:int
    metric7:int
    metric8:int
    metric9:int


class MaintenanceRequest(BaseModel):
    equipment_id: str
    maintenance_type: str
    scheduled_time: datetime
    priority: Optional[int] = 1
    title: Optional[int] = 1
    description: str

class PredictionRequest(BaseModel):
    equipment_id: str
    
class CreateSensorDataRequest(BaseModel):
    equipment_id: str
    device: str
    metric1:int
    metric2:int
    metric3:int
    metric4:int
    metric5:int
    metric6:int
    metric7:int
    metric8:int
    metric9:int

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

class PyObjectId(str):
    """Custom ObjectId field for Pydantic."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

class CreateNotificationRequest(BaseModel):
     
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    maintenance_task_id: PyObjectId
    equipment_id: PyObjectId
    user_id: PyObjectId
    notification_type: str = Field(..., pattern="^(Reminder|Warning|Critical)$")
    message: str
    title: str
    status: str = Field("unread", pattern="^(unread|read|acknowledged)$")
    priority: int = Field(..., ge=1, le=5)
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None

    
    