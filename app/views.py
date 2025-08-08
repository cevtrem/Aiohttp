from aiohttp import web
from sqlalchemy.future import select
from sqlalchemy import update, delete, func
from app.database import async_session
from app.models import Advertisement, User
from app.schemas import (
    AdvertisementCreateSchema, AdvertisementUpdateSchema, 
    AdvertisementResponseSchema, AdvertisementListResponseSchema,
    UserCreateSchema, UserResponseSchema, LoginSchema, TokenResponseSchema
)
from app.auth import require_auth, register_user, authenticate_user, create_access_token
from pydantic import ValidationError
import math
from sqlalchemy.orm import selectinload


async def register(request):
    """Регистрация нового пользователя"""
    try:
        data = await request.json()
        user_data = UserCreateSchema(**data)
        user = await register_user(user_data)
        
        return web.json_response(
            UserResponseSchema.model_validate(user).model_dump(),
            status=201
        )
    except ValidationError as e:
        return web.json_response({"error": "Validation error", "details": e.errors()}, status=400)
    except web.HTTPConflict as e:
        return web.json_response({"error": str(e.reason)}, status=409)
    except Exception as e:
        return web.json_response({"error": "Internal server error"}, status=500)


async def login(request):
    """Аутентификация пользователя"""
    try:
        data = await request.json()
        login_data = LoginSchema(**data)
        user = await authenticate_user(login_data)
        
        access_token = create_access_token(data={"sub": user.username})
        
        return web.json_response(
            TokenResponseSchema(access_token=access_token).model_dump(),
            status=200
        )
    except ValidationError as e:
        return web.json_response({"error": "Validation error", "details": e.errors()}, status=400)
    except web.HTTPUnauthorized as e:
        return web.json_response({"error": str(e.reason)}, status=401)
    except Exception as e:
        return web.json_response({"error": "Internal server error"}, status=500)


@require_auth
async def create_ad(request):
    """Создание нового объявления"""
    try:
        data = await request.json()
        ad_data = AdvertisementCreateSchema(**data)
        
        # Проверяем существование пользователя
        async with async_session() as session:
            result = await session.execute(select(User).where(User.id == ad_data.owner_id))
            user = result.scalar()
            if not user:
                return web.json_response({"error": "User not found"}, status=404)
            
            ad = Advertisement(
                title=ad_data.title,
                description=ad_data.description,
                owner_id=ad_data.owner_id
            )
            session.add(ad)
            await session.commit()
            await session.refresh(ad)
            
            # Получаем объявление с загруженным пользователем
            result = await session.execute(
                select(Advertisement)
                .options(selectinload(Advertisement.owner_user))
                .where(Advertisement.id == ad.id)
            )
            ad_with_owner = result.scalar()
            
            return web.json_response(
                AdvertisementResponseSchema.model_validate(ad_with_owner).model_dump(),
                status=201
            )
    except ValidationError as e:
        return web.json_response({"error": "Validation error", "details": e.errors()}, status=400)
    except Exception as e:
        return web.json_response({"error": "Internal server error"}, status=500)


async def get_ads(request):
    """Получение списка объявлений с пагинацией"""
    try:
        page = int(request.query.get('page', 1))
        per_page = min(int(request.query.get('per_page', 10)), 100)  # Максимум 100 на страницу
        
        if page < 1 or per_page < 1:
            return web.json_response({"error": "Invalid pagination parameters"}, status=400)
        
        async with async_session() as session:
            # Подсчитываем общее количество объявлений
            total_result = await session.execute(select(func.count(Advertisement.id)))
            total = total_result.scalar()
            
            # Вычисляем количество страниц
            pages = math.ceil(total / per_page)
            
            # Получаем объявления с пагинацией
            offset = (page - 1) * per_page
            result = await session.execute(
                select(Advertisement)
                .options(selectinload(Advertisement.owner_user))
                .order_by(Advertisement.created_at.desc())
                .offset(offset)
                .limit(per_page)
            )
            ads = result.scalars().all()
            
            # Преобразуем в схемы ответа
            ads_data = [AdvertisementResponseSchema.model_validate(ad).model_dump() for ad in ads]
            
            return web.json_response(
                AdvertisementListResponseSchema(
                    items=ads_data,
                    total=total,
                    page=page,
                    per_page=per_page,
                    pages=pages
                ).model_dump()
            )
    except ValueError as e:
        return web.json_response({"error": "Invalid pagination parameters"}, status=400)
    except Exception as e:
        return web.json_response({"error": "Internal server error"}, status=500)


async def get_ad(request):
    """Получение конкретного объявления"""
    try:
        ad_id = int(request.match_info['ad_id'])
        
        async with async_session() as session:
            result = await session.execute(
                select(Advertisement)
                .options(selectinload(Advertisement.owner_user))
                .where(Advertisement.id == ad_id)
            )
            ad = result.scalar()
            
            if not ad:
                return web.json_response({"error": "Advertisement not found"}, status=404)
            
            return web.json_response(
                AdvertisementResponseSchema.model_validate(ad).model_dump()
            )
    except ValueError:
        return web.json_response({"error": "Invalid advertisement ID"}, status=400)
    except Exception as e:
        return web.json_response({"error": "Internal server error"}, status=500)


@require_auth
async def update_ad(request):
    """Полное обновление существующего объявления (PUT)"""
    try:
        ad_id = int(request.match_info['ad_id'])
        data = await request.json()
        
        # Валидируем данные
        update_data = AdvertisementUpdateSchema(**data)
        
        async with async_session() as session:
            # Проверяем существование объявления
            result = await session.execute(
                select(Advertisement).where(Advertisement.id == ad_id)
            )
            ad = result.scalar()
            
            if not ad:
                return web.json_response({"error": "Advertisement not found"}, status=404)
            
            # Проверяем права доступа (только владелец может редактировать)
            current_user = request['user']
            if ad.owner_id != current_user.id:
                return web.json_response({"error": "Access denied"}, status=403)
            
            # Обновляем объявление
            update_values = {}
            if update_data.title is not None:
                update_values['title'] = update_data.title
            if update_data.description is not None:
                update_values['description'] = update_data.description
            
            if update_values:
                await session.execute(
                    update(Advertisement)
                    .where(Advertisement.id == ad_id)
                    .values(**update_values)
                )
                await session.commit()
            
            # Возвращаем обновленное объявление
            result = await session.execute(
                select(Advertisement)
                .options(selectinload(Advertisement.owner_user))
                .where(Advertisement.id == ad_id)
            )
            updated_ad = result.scalar()
            
            return web.json_response(
                AdvertisementResponseSchema.model_validate(updated_ad).model_dump()
            )
    except ValidationError as e:
        return web.json_response({"error": "Validation error", "details": e.errors()}, status=400)
    except ValueError:
        return web.json_response({"error": "Invalid advertisement ID"}, status=400)
    except Exception as e:
        return web.json_response({"error": "Internal server error"}, status=500)


@require_auth
async def delete_ad(request):
    """Удаление объявления"""
    try:
        ad_id = int(request.match_info['ad_id'])
        
        async with async_session() as session:
            # Проверяем существование объявления
            result = await session.execute(
                select(Advertisement).where(Advertisement.id == ad_id)
            )
            ad = result.scalar()
            
            if not ad:
                return web.json_response({"error": "Advertisement not found"}, status=404)
            
            # Проверяем права доступа (только владелец может удалять)
            current_user = request['user']
            if ad.owner_id != current_user.id:
                return web.json_response({"error": "Access denied"}, status=403)
            
            # Удаляем объявление
            await session.execute(
                delete(Advertisement).where(Advertisement.id == ad_id)
            )
            await session.commit()
            
            return web.json_response(
                {"message": "Advertisement deleted successfully"},
                status=200
            )
    except ValueError:
        return web.json_response({"error": "Invalid advertisement ID"}, status=400)
    except Exception as e:
        return web.json_response({"error": "Internal server error"}, status=500)
