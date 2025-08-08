import jwt
import bcrypt
from datetime import datetime, timedelta
from aiohttp import web
from functools import wraps
from app.models import User
from app.database import async_session
from sqlalchemy.future import select
from app.schemas import UserCreateSchema, LoginSchema


# Секретный ключ для JWT (в продакшене должен быть в переменных окружения)
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    """Хеширование пароля"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str) -> User:
    """Получение текущего пользователя по токену"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise web.HTTPUnauthorized(reason="Invalid token")
    except jwt.PyJWTError:
        raise web.HTTPUnauthorized(reason="Invalid token")
    
    async with async_session() as session:
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalar()
        if user is None:
            raise web.HTTPUnauthorized(reason="User not found")
        return user


def require_auth(f):
    """Декоратор для защиты эндпоинтов"""
    @wraps(f)
    async def decorated_function(request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise web.HTTPUnauthorized(reason="Missing or invalid authorization header")
        
        token = auth_header.split(' ')[1]
        user = await get_current_user(token)
        request['user'] = user
        return await f(request)
    return decorated_function


async def register_user(user_data: UserCreateSchema) -> User:
    """Регистрация нового пользователя"""
    async with async_session() as session:
        # Проверяем, что пользователь не существует
        result = await session.execute(
            select(User).where(
                (User.username == user_data.username) | (User.email == user_data.email)
            )
        )
        if result.scalar():
            raise web.HTTPConflict(reason="Username or email already exists")
        
        # Создаем нового пользователя
        hashed_password = hash_password(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password
        )
        session.add(user)
        await session.commit()
        return user


async def authenticate_user(login_data: LoginSchema) -> User:
    """Аутентификация пользователя"""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.username == login_data.username)
        )
        user = result.scalar()
        
        if not user or not verify_password(login_data.password, user.password_hash):
            raise web.HTTPUnauthorized(reason="Invalid username or password")
        
        return user
