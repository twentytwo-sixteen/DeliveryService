"""add_package_types

Revision ID: 15b557f30f39
Revises: 671e97022596
Create Date: 2025-06-08 06:03:34.660414

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15b557f30f39'
down_revision: Union[str, None] = '671e97022596'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Создаем временную таблицу для данных
    package_types = op.create_table(
        'temp_package_types',
        sa.Column('id', sa.Integer, nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
    )

    # Вставляем данные
    op.bulk_insert(
        package_types,
        [
            {"id": 1, "name": "Документы"},
            {"id": 2, "name": "Электроника"},
            {"id": 3, "name": "Одежда"},
            {"id": 4, "name": "Косметика"},
            {"id": 5, "name": "Продукты питания"},
            {"id": 6, "name": "Хрупкие товары"},
            {"id": 7, "name": "Книги"},
            {"id": 8, "name": "Аптечка"},
            {"id": 9, "name": "Спортинвентарь"},
            {"id": 10, "name": "Ювелирные изделия"}
        ]
    )

    # Переносим данные в основную таблицу (если она уже существует)
    op.execute("""
        INSERT INTO package_types (id, name)
        SELECT id, name FROM temp_package_types
        ON CONFLICT (id) DO NOTHING
    """)
    
    # Удаляем временную таблицу
    op.drop_table('temp_package_types')



def downgrade():
    # Удаляем добавленные записи
    op.execute("DELETE FROM package_types WHERE id BETWEEN 1 AND 10")
