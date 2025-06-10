from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from src.app.db.models.base import Base

class PackageType(Base):
    __tablename__ = "package_types"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)