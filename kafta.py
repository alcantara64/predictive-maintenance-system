# kafta.py
from confluent_kafka import Producer, Consumer, KafkaError
from config import KAFKA_BOOTSTRAP_SERVERS


class KaftaService:
    
    def __init__(self):
        print("Kafka server:", KAFKA_BOOTSTRAP_SERVERS)
        self._producer = self._create_producer()

    def _create_producer(self):
        conf = {
            'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'fastapi-producer'
        }
        return Producer(conf)

    def get_producer(self):
        return self._producer

    def create_consumer(self):
        conf = {
            'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
            'group.id': 'fastapi-consumer',
            'auto.offset.reset': 'earliest'
        }
        return Consumer(conf)

    def get_error_class(self):
        return KafkaError
