from confluent_kafka import Producer, Consumer, KafkaError

from config import KAFKA_BOOTSTRAP_SERVERS


class KaftaService:
    
    def producer(self):
        conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'client.id': 'fastapi-producer'
            }
        return Producer(conf)
    
    def consumer():
        conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'fastapi-consumer',
        'auto.offset.reset': 'earliest'
         }
        return Consumer(conf)
    
    def error():
        return KafkaError