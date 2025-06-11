import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.db.models import PackageType
from src.app.services.package_type import get_all_package_types

@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)

def mock_execute_with_types(types):
    """Создает цепочку execute().scalars().all() для моков."""
    mock_all = AsyncMock(return_value=types)

    mock_scalars = MagicMock()
    mock_scalars.all = mock_all

    mock_result = MagicMock()
    mock_result.scalars = MagicMock(return_value=mock_scalars)

    return AsyncMock(return_value=mock_result)

@pytest.mark.asyncio
async def test_get_all_package_types_success(mock_session):
    mock_types = [
        PackageType(id=1, name="Электроника"),
        PackageType(id=2, name="Документы")
    ]
    mock_session.execute = mock_execute_with_types(mock_types)

    result = await get_all_package_types(
        session=mock_session,
        skip=0,
        limit=5
    )

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].name == "Электроника"
    assert result[1].name == "Документы"
    mock_session.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_all_package_types_pagination(mock_session):
    all_types = [PackageType(id=i, name=f"Тип {i}") for i in range(1, 6)]
    paginated_types = all_types[2:4]  # Тип 3 и Тип 4

    mock_session.execute = mock_execute_with_types(paginated_types)

    result = await get_all_package_types(
        session=mock_session,
        skip=2,
        limit=2
    )

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].id == 3
    assert result[1].id == 4
    mock_session.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_all_package_types_empty(mock_session):
    mock_session.execute = mock_execute_with_types([])

    result = await get_all_package_types(
        session=mock_session,
        skip=100,
        limit=10
    )

    assert isinstance(result, list)
    assert len(result) == 0
    mock_session.execute.assert_awaited_once()
