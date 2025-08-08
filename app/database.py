from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:////data/ads.db")

engine = create_async_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30
    },
    pool_pre_ping=True,
    echo=True
)

async_session = sessionmaker(engine, expire_on_commit=False,
                             class_=AsyncSession)
