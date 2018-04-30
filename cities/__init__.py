import logging
import os

from graphql.execution.executors.asyncio import AsyncioExecutor

from sanic import Sanic
from sanic_graphql import GraphQLView

import asyncpg

from .loaders import CountryLoader, CityLoader
from .schema import build_schema

logger = logging.getLogger(__name__)

app = Sanic()

DSN = os.environ.get('DATABASE_URL')


@app.listener('before_server_start')
async def register_db(app, loop):
    logger.info('Registering pool')
    if DSN is None:
        raise RuntimeError('export DATABASE_URL before running this script')

    app.pool = await asyncpg.create_pool(DSN, loop=loop, min_size=1, max_size=2)


@app.listener('after_server_stop')
async def close_db(app, loop):
    await app.pool.close()


@app.middleware('request')
async def acquire_db(request):
    request['db'] = await request.app.pool.acquire()


@app.middleware('request')
async def setup_loaders(request):
    request['loaders'] = {
        'Country': CountryLoader(request['db']),
        'City': CityLoader(request['db'])
    }


@app.middleware('response')
async def release_db(request, response):
    await request.app.pool.release(request['db'])


@app.listener('before_server_start')
async def init_graphql(app, loop):
    schema = build_schema()

    app.add_route(
        GraphQLView.as_view(
            schema=schema,
            executor=AsyncioExecutor(loop=loop),
            graphiql=True
        ),
        '/graphql',
        methods=['POST', 'OPTIONS']
    )
