from sqlalchemy import ForeignKey, Numeric, String, Float, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.app.db.models.base import Base
from src.app.db.models.package_type import PackageType
from src.app.db.models.company import Company

class Package(Base):
    __tablename__ = "packages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    content_price_usd: Mapped[float] = mapped_column(Float, nullable=False)
    delivery_price_rub: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    session_id: Mapped[str] = mapped_column(String(255), nullable=False)  # сессия пользователя

    type_id: Mapped[int] = mapped_column(ForeignKey("package_types.id"), nullable=False)
    type: Mapped[PackageType] = relationship(backref="packages")

    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"), nullable=True)
    company: Mapped[Company] = relationship(backref="packages", lazy="select")
