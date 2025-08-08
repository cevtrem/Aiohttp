from aiohttp import web
from app.views import (
    create_ad, get_ad, update_ad, delete_ad, get_ads,
    register, login
)


def setup_routes(app):
    # Аутентификация
    app.router.add_post('/auth/register', register)
    app.router.add_post('/auth/login', login)
    
    # Объявления
    app.router.add_post('/ads', create_ad)
    app.router.add_get('/ads', get_ads)
    app.router.add_get(r'/ads/{ad_id:\d+}', get_ad)
    app.router.add_put(r'/ads/{ad_id:\d+}', update_ad)
    app.router.add_delete(r'/ads/{ad_id:\d+}', delete_ad)


async def init_app():
    app = web.Application()
    setup_routes(app)
    return app
