def single_maintenance_data_serial(maintenance) -> dict:
    return {
        "id": str(maintenance["_id"])
    }

def list_maintenance_data(maintenances) -> list:
    return[single_maintenance_data_serial(maintenances) for maintenance in maintenances]