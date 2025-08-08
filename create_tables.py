#!/usr/bin/env python3
import asyncio
from app.models import Base
from app.database import engine


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Таблицы созданы успешно!")


if __name__ == "__main__":
    asyncio.run(create_tables())
