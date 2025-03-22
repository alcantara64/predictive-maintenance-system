from fastapi import APIRouter, HTTPException
from model.pydantic import MaintenanceRequest
from utils.notification import send_notification

maintenance_router = APIRouter()
maintenance_schedule = []

@maintenance_router.post("/schedule")
async def schedule_maintenance(request: MaintenanceRequest):
    maintenance_schedule.append(request.dict())
    message = f"Maintenance scheduled for equipment {request.equipment_id} at {request.scheduled_time}."
    await send_notification(message)
    return {"message": "Maintenance scheduled successfully"}

@maintenance_router.get("/schedule")
async def get_maintenance_schedule():
    return {"maintenance_schedule": maintenance_schedule}