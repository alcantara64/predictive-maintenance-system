from fastapi import APIRouter
from db import database_handler
from config import COLLECTIONS

dashboard_router = APIRouter()

@dashboard_router.get("/")
async def get_dashboard():
    user_count = database_handler.get_document_count(collection=COLLECTIONS.get('user'), query={})
    equipment_count = database_handler.get_document_count(collection=COLLECTIONS.get('equipment'), query={})
    maintenance_count = database_handler.get_document_count(collection=COLLECTIONS.get('maintenance'), query={})

    return {"equipment": equipment_count, "user": user_count, "maintenance_request": maintenance_count}
