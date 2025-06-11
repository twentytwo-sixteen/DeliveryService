import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from src.app.db.models import Package, PackageType
from src.app.schemas.parcel import PackageCreate
from src.app.services.parcel import (
    create_package,
    get_packages,
    get_package_by_id
)

# Фикстура
@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.execute = AsyncMock()
    session.get = AsyncMock()
    session.add = MagicMock()
    return session

@pytest.fixture
def sample_package_data():
    return PackageCreate(
        title="Телефон",
        weight_kg=0.3,
        content_price_usd=999.99,
        type_id=1
    )

# ---- create_package ----

@pytest.mark.asyncio
async def test_create_package_success(mock_session, sample_package_data):
    mock_package_type = PackageType(id=1, name="Электроника")
    mock_session.get = AsyncMock(return_value=mock_package_type)

    mock_package = Package(
        id=1,
        title=sample_package_data.title,
        weight_kg=sample_package_data.weight_kg,
        content_price_usd=sample_package_data.content_price_usd,
        type_id=sample_package_data.type_id,
        session_id="test_session"
    )

    mock_result = MagicMock()
    mock_result.scalar_one = MagicMock(return_value=mock_package)  # <- Вот здесь

    mock_session.execute = AsyncMock(return_value=mock_result)

    # Вызываем тестируемую функцию
    result = await create_package(
        session=mock_session,
        data=sample_package_data,
        session_id="test_session"
    )

    assert result.id == 1
    assert result.title == "Телефон"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()

# ---- get_packages ----

@pytest.mark.asyncio
async def test_get_packages_with_filters(mock_session):
    mock_packages = [
        MagicMock(spec=Package, id=1, title="Посылка 1", type=MagicMock(name="Тип 1")),
        MagicMock(spec=Package, id=2, title="Посылка 2", type=MagicMock(name="Тип 2"))
    ]

    mock_execute_result = MagicMock()
    mock_execute_result.unique.return_value.scalars.return_value.all = MagicMock(return_value=mock_packages)
    mock_session.execute.return_value = mock_execute_result

    result = await get_packages(
        session=mock_session,
        session_id="test_session",
        type_id=1,
        has_delivery_price=True,
        limit=2,
        offset=0
    )

    assert len(result) == 2
    assert result[0].id == 1
    mock_session.execute.assert_awaited_once()


# ---- get_package_by_id ----

@pytest.mark.asyncio
async def test_get_package_by_id_success(mock_session):
    mock_package = MagicMock(
        spec=Package,
        id=1,
        title="Тестовая посылка",
        session_id="test_session",
        type=MagicMock(name="Тип")
    )

    mock_execute_result = MagicMock()
    mock_execute_result.unique.return_value.scalar_one_or_none = MagicMock(return_value=mock_package)
    mock_session.execute.return_value = mock_execute_result

    result = await get_package_by_id(
        session=mock_session,
        package_id=1,
        session_id="test_session"
    )

    assert result.id == 1
    assert result.title == "Тестовая посылка"
    mock_session.execute.assert_awaited_once()

