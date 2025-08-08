from app import init_app
import asyncio
from aiohttp import web
from app.models import Base
from app.database import engine


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def start():
    await init_db()
    app = await init_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("Server started at http://0.0.0.0:8080")
    while True:
        await asyncio.sleep(3600)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
