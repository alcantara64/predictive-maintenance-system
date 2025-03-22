from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db import database_handler
from kafta import KaftaService


from api.authentication import auth_router
from api.equipment import equipment_router
from api.maintenance import maintenance_router
from api.sensor_data import sensor_data_router
from api.dashboard import dashboard_router
from api.users import user_router

origins = [
    "http://localhost:3000", 
    "*",  # Allow all (use with caution)
]

# Database initialization
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

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(equipment_router, prefix="/equipment", tags=["Equipment"])
app.include_router(maintenance_router, prefix="/maintenance", tags=["Maintenance"])
app.include_router(sensor_data_router, prefix="/sensor-data", tags=["Sensor Data"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(user_router, prefix="/users", tags=["Users"])

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)