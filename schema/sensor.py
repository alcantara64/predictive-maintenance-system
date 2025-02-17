def single_sensor_data_serial(sensor) -> dict:
    return {
        "id": str(sensor["_id"])
    }

def list_sensor(sensors) -> list:
    return[single_sensor_data_serial(sensors) for sensor in sensors]