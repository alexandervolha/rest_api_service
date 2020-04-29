import asyncio
import logging
import json

from rest_api_service.kafka import AIOKafkaProducerCtx, AIOKafkaConsumerCtx
from rest_api_service.server import run_server
from rest_api_service.settings import KAFKA_SERVER
from rest_api_service.utils import setup_logging


async def main():
    setup_logging()
    logging.info('Waiting for kafka topics creation...')
    await asyncio.sleep(15)  # wait for topics creation
    logging.info('Rest API service started.')
    try:
        synchronization_events = {}
        articles_storage = {}
        async with \
                AIOKafkaProducerCtx(bootstrap_servers=KAFKA_SERVER) as kafka_producer,\
                AIOKafkaConsumerCtx('response_topic', bootstrap_servers=KAFKA_SERVER) as kafka_consumer,\
                run_server(kafka_producer, synchronization_events, articles_storage):
            async for msg in kafka_consumer:
                await process_message(msg, synchronization_events, articles_storage)

    finally:
        logging.info('Rest API service stopped.')


async def process_message(msg, synchronization_events, articles_storage):
    key = msg.key.decode('utf-8')
    event = synchronization_events.pop(key, None)
    if not event:
        return
    value = json.loads(msg.value.decode('utf-8'))
    articles_storage[key] = value
    event.set()


if __name__ == '__main__':
    asyncio.run(main())
