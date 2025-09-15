from __future__ import annotations

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncIterator

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from auth_service.main import app
from auth_service.src.db.session import get_db as real_get_db
from shared.src.models.base import Base
# Ensure all models are imported so relationships resolve before metadata.create_all
import shared.src.models.user  # noqa: F401
import shared.src.models.user_preference  # noqa: F401
import shared.src.models.subscription  # noqa: F401
import shared.src.models.ai_companion  # noqa: F401
import shared.src.models.conversation  # noqa: F401
import shared.src.models.message  # noqa: F401
import shared.src.models.hologram_device  # noqa: F401
import shared.src.models.character_asset  # noqa: F401
import shared.src.models.animation_sequence  # noqa: F401
import shared.src.models.voice_profile  # noqa: F401


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture()
async def db_session(test_engine) -> AsyncIterator[AsyncSession]:
    SessionLocal = sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    async with SessionLocal() as session:
        yield session


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    # Override DB dependency with in-memory sqlite session
    async def override_get_db():
        yield db_session

    app.dependency_overrides[real_get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.pop(real_get_db, None)


