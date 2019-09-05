import asyncpgsa
import asyncpg
from aiopg.sa import create_engine

import asyncio
import jinja2
import aiohttp_jinja2
from aiohttp import web

from .routes import setup_static_routes
from .views import routes
from .middlewares import check_api_key
from .db import create_db


# async def init_app(config):
async def init_app(config):
    app = web.Application(middlewares=[check_api_key])
    # app = web.Application()

    app['config'] = config

    aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('mmapp', 'templates'))

    app.add_routes(routes)

    setup_static_routes(app)

    app.on_startup.append(on_start)
    app.on_cleanup.append(on_close)

    return app


# async def create_app(config: dict):
async def create_app(config):
    # app = await init_app(config)
    app = await init_app(config)
    return app


async def on_start(app):
    # conf = app['config']
    # app['db'] = await asyncpg.pool.create_pool(dsn='postgresql://mmapp:mmapp1234@localhost:5432/mmappdb')
    app['db'] = await asyncpg.connect(host='mmappdb', user='mmapp', password='mmapp1234', database='mmappdb')
    # engine = await create_engine(
    #     database='mmappdb',
    #     user='mmapp',
    #     password='mmapp1234',
    #     host='localhost',
    #     port='5432')
    # app['db'] = engine
    # await create_db(app)


async def on_close(app):
    await app['db'].close()
