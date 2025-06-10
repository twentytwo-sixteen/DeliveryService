from sqlalchemy.orm import Mapped, mapped_column
from src.app.db.models.base import Base

class Company(Base):
    __tablename__ = "companies"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    