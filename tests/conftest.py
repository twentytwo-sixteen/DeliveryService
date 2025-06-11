import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.app.db.models.base import Base
from src.app.db.models import PackageType

@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    await engine.dispose()

@pytest.fixture
async def session(engine):
    async with AsyncSession(engine) as session:
        yield session

@pytest.fixture(autouse=True)
async def setup_db(session):
    # Добавляем тестовые данные
    package_types = [
        PackageType(id=1, name="Электроника"),
        PackageType(id=2, name="Документы")
    ]
    session.add_all(package_types)
    await session.commit()
    yield
    # Очистка после теста
    await session.rollback()