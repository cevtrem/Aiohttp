from aiohttp import web
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.database import async_session
from app.models import Advertisement


async def create_ad(request):
    """Создание нового объявления"""
    data = await request.json()
    async with async_session() as session:
        ad = Advertisement(
            title=data['title'],
            description=data['description'],
            owner=data['owner']
        )
        session.add(ad)
        await session.commit()
        return web.json_response({
            "id": ad.id,
            "title": ad.title,
            "description": ad.description,
            "created_at": ad.created_at.isoformat(),
            "owner": ad.owner
        }, status=201)


async def get_ad(request):
    ad_id = int(request.match_info['ad_id'])
    async with async_session() as session:
        result = await session.execute(select(Advertisement).where(Advertisement.id == ad_id))
        ad = result.scalar()
        if not ad:
            return web.json_response({"error": "Advertisement not found"}, status=404)
        return web.json_response({
            "id": ad.id,
            "title": ad.title,
            "description": ad.description,
            "created_at": ad.created_at.isoformat(),
            "owner": ad.owner
        })


async def update_ad(request):
    """Обновление существующего объявления"""
    ad_id = int(request.match_info['ad_id'])
    data = await request.json()

    async with async_session() as session:
        # Проверяем существование объявления
        result = await session.execute(
            select(Advertisement).where(Advertisement.id == ad_id))
        ad = result.scalar()

        if not ad:
            return web.json_response(
                {"error": "Advertisement not found"},
                status=404
            )

        # Обновляем только переданные поля
        update_data = {}
        if 'title' in data:
            update_data['title'] = data['title']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'owner' in data:
            update_data['owner'] = data['owner']

        if update_data:
            await session.execute(
                update(Advertisement)
                .where(Advertisement.id == ad_id)
                .values(**update_data)
            )
            await session.commit()

        # Возвращаем обновленное объявление
        result = await session.execute(
            select(Advertisement).where(Advertisement.id == ad_id))
        updated_ad = result.scalar()

        return web.json_response({
            "id": updated_ad.id,
            "title": updated_ad.title,
            "description": updated_ad.description,
            "created_at": updated_ad.created_at.isoformat(),
            "owner": updated_ad.owner
        })


async def delete_ad(request):
    """Удаление объявления"""
    ad_id = int(request.match_info['ad_id'])

    async with async_session() as session:
        # Проверяем существование объявления
        result = await session.execute(
            select(Advertisement).where(Advertisement.id == ad_id))
        ad = result.scalar()

        if not ad:
            return web.json_response(
                {"error": "Advertisement not found"},
                status=404
            )

        # Удаляем объявление
        await session.execute(
            delete(Advertisement).where(Advertisement.id == ad_id))
        await session.commit()

        return web.json_response(
            {"message": "Advertisement deleted successfully"},
            status=200
        )
