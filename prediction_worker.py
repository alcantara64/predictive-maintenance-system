# prediction_worker.py

import json
import pandas as pd
from confluent_kafka import KafkaException
from kafta import KaftaService
from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, COLLECTIONS
from db import database_handler
from machine_learning import model, scaler


class SensorPredictor:
    def __init__(self, kafka_service: KaftaService):
        self.consumer = kafka_service.create_consumer()
        self.consumer.subscribe([KAFKA_TOPIC])
        self.feature_names = [
             'metric1', 'metric2',
            'metric3', 'metric4', 'metric5',
            'metric6', 'metric7', 'metric8', 'metric9'
        ]

    def run(self):
        print(f"Kafka consumer started. Listening to topic: {KAFKA_TOPIC}")
        while True:
           
            msg = self.consumer.poll(timeout=1.0)
            if msg is None:
                print("⏳ No message received.")
                continue

            if msg.error():
                print(f"Kafka error: {msg.error()}")
                continue

            try:
                data = json.loads(msg.value().decode("utf-8"))
                print(f"Received sensor data: {data}")
                self.process_message(data)
            except KafkaException as ke:
                print(f"Kafka exception: {ke}")
            except Exception as e:
                print(f"General error: {e}")

    def process_message(self, sensor_data: dict):
        try:
            input_data = [[
                sensor_data['metric1'],
                sensor_data['metric2'],
                sensor_data['metric3'],
                sensor_data['metric4'],
                sensor_data['metric5'],
                sensor_data['metric6'],
                sensor_data['metric7'],
                sensor_data['metric8'],
                sensor_data['metric9'],
            ]]

            df = pd.DataFrame(input_data, columns=self.feature_names)
            input_scaled = scaler.transform(df)
            prediction = model.predict(input_scaled)
            confidence = float(model.predict_proba(input_scaled)[0][1])

            if prediction[0] == 1:
                print(f"Failure predicted for machine {sensor_data.get('equipment_id')}, confidence: {confidence:.2f}")
                self.save_maintenance_request(sensor_data, confidence)
            else:
                print("No failure predicted.")

        except KeyError as ke:
            print(f" Missing required field in sensor data: {ke}")
        except Exception as e:
            print(f" Failed to process message: {e}")

    def save_maintenance_request(self, sensor_data, confidence):
        document = {
            "equipment_id": sensor_data.get("equipment_id"),
            "prediction": "FAILURE",
            "confidence": confidence,
            "sensor_data": sensor_data,
            "title":"AI-Predicting Failure",
            "priority":4
        }
        database_handler.insert_document(
            collection=COLLECTIONS.get('maintenance'),
            document=document
        )
        print(f"📝 Maintenance request saved: {document['equipment_id']}")



if __name__ == "__main__":
    try:
        print("🚀 Starting prediction worker...")
        kafka_service = KaftaService()
        predictor = SensorPredictor(kafka_service)
        predictor.run()
    except Exception as e:
        print(f"❌ Failed to start worker: {e}")
