import logging
import time
import asyncio
from contextlib import asynccontextmanager

from aiohttp import web


@asynccontextmanager
async def run_server(kafka_producer, synchronization_events, articles_storage):
    app = web.Application()
    handler = Handler(kafka_producer, synchronization_events, articles_storage)
    app.add_routes([web.get('/articles', handler.get_articles)])
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner).start()
    try:
        yield
    finally:
        await runner.clean_up()


class Handler:
    def __init__(self, kafka_producer, synchronization_events, articles_storage):
        self.kafka_producer = kafka_producer
        self.synchronization_events = synchronization_events
        self.articles_storage = articles_storage

    async def get_articles(self, request):
        request_params = request.query
        query_str = request_params.get('query_str')
        if not query_str:
            raise web.HTTPBadGateway()

        current_ts = time.time()
        key = f'{query_str}-{current_ts}'
        await self.kafka_producer.send('request_topic', value=bytes(query_str, 'utf-8'), key=bytes(key, 'utf-8'))
        logging.info(f'{query_str} was sent to kafka')
        event = asyncio.Event()
        self.synchronization_events[key] = event
        await event.wait()
        articles = self.articles_storage.pop(key)
        return web.json_response(articles)
