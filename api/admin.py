from fastapi import APIRouter, HTTPException
from config import COLLECTIONS
from model.pydantic import MaintenanceRequest
from utils.notification import send_notification
from db import database_handler
from bson.objectid import ObjectId
maintenance_router = APIRouter()
maintenance_schedule = []

@maintenance_router.post("/users")
async def schedule_maintenance(request: MaintenanceRequest):
   
    try:
        scheduled_maintenance_id = database_handler.insert_document(collection=COLLECTIONS.get('maintenance'), document=request.model_dump())
        equipment = database_handler.find_one_document(collection=COLLECTIONS.get('equipment'), query={"_id": ObjectId(request.equipment_id)})
        message = f"Maintenance scheduled for equipment {equipment['name']} at {request.scheduled_time}."
        if scheduled_maintenance_id :
            database_handler.insert_document(collection=COLLECTIONS.get('notification'), document={'maintenance_task_id':scheduled_maintenance_id,'equipment_id':request.equipment_id, "status":"unread", 'priority':request.priority, "title":message, "details": request.description   })
            await send_notification(message)
        return {"message": "Maintenance scheduled successfully"}
    except Exception as e:
         print(e)
         raise HTTPException(status_code=500, detail="Server error occurred, try again letter")

@maintenance_router.get("/schedule")
async def get_maintenance_schedule():
    return {"maintenance_schedule": maintenance_schedule}

@maintenance_router.get("/notifications")
async def get_notifications():
    try:
        notifications = database_handler.find_documents(collection=COLLECTIONS.get('notification'))
        return {"data": notifications}
    except Exception as e:
         print(e)
         raise HTTPException(status_code=500, detail="Server error occurred, try again letter")
