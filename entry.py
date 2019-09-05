import argparse
import asyncio
from aiohttp import web
from mmapp import create_app
from mmapp.db import create_db
from mmapp.settings import get_config

# try:
#     import uvloop
#     asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
# except ImportError:
#     print('Error while import uvloop')


# parser = argparse.ArgumentParser(description='Music Manager Application')
# parser.add_argument('--host', help='Host to listen', default='0.0.0.0')
# parser.add_argument('--port', help='Post to accept connection', default=8080)
# parser.add_argument('--reload', action='store_true', help='Autoreload code on change', default='--reload')
# parser.add_argument('-c', '--config', type=argparse.FileType('r'), help='Path to configuration file')


# args = parser.parse_args()

asyncio.get_event_loop().run_until_complete(create_db())

# app = create_app(get_config(args.config))


async def crapp():
    # app = create_app(get_config(args.config))
    app = await create_app(get_config())
    return app


# if args.reload:
#     print('Start with code reload')
#     import aioreloader
#     aioreloader.start()


# if __name__ == '__main__':
#     web.run_app(app, host=args.host, port=args.port)
# web.run_app(app, host=args.host, port=args.port)
