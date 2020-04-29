import asyncio
import logging

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from kafka.errors import KafkaError

from rest_api_service.utils import async_retry


class AIOKafkaProducerCtx(AIOKafkaProducer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, loop=asyncio.get_event_loop())

    async def __aenter__(self):
        logging.info('Kafka producer starting...')
        await async_retry()(self.start)()
        logging.info('Kafka producer started.')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logging.info('Kafka producer stopping...')
        try:
            await self.stop()
        except (KafkaError, asyncio.TimeoutError) as e:
            logging.error(f'Failed to stop kafka producer ({repr(e)})')
        else:
            logging.info('Kafka producer stopped')


class AIOKafkaConsumerCtx(AIOKafkaConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, loop=asyncio.get_event_loop())

    async def __aenter__(self):
        logging.info('Kafka consumer starting...')
        await async_retry()(self.start)()
        logging.info('Kafka consumer started.')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logging.info('Kafka consumer stopping...')
        try:
            await self.stop()
        except (KafkaError, asyncio.TimeoutError) as e:
            logging.error(f'Failed to stop kafka consumer ({repr(e)}).')
        else:
            logging.info('Kafka consumer stopped.')
