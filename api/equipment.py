from fastapi import APIRouter, HTTPException
from model.pydantic import CreateEquipmentRequest
from db import database_handler
from config import COLLECTIONS

equipment_router = APIRouter()

@equipment_router.post("/")
async def create_equipment(equipmentRequest: CreateEquipmentRequest):
    does_equipment_exist = database_handler.find_one_document(collection=COLLECTIONS.get('equipment'), query={'model_number': equipmentRequest.model_number, 'serial_number': equipmentRequest.serial_number} )
    if does_equipment_exist :
         raise HTTPException(status_code=400, detail="Equipment already exist")
     
    equipment = database_handler.insert_document(collection=COLLECTIONS.get('equipment'), document=dict(equipmentRequest))
    if equipment is None:
        raise HTTPException(status_code=500, detail="Could not create equipment")
    return {"message": 'Equipment created successfully'}

@equipment_router.get("/")
async def get_equipments():
    equipments = database_handler.find_documents(collection=COLLECTIONS.get('equipment'))
    if equipments is None:
        raise HTTPException(status_code=500, detail="Could not fetch equipments")
    return {"data": equipments}
