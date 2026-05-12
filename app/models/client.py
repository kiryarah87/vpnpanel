from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .subscription import Subscription


class Client(Base, TimestampMixin):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str | None] = mapped_column(String(256), unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    traffic_limit_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    used_traffic_bytes: Mapped[int] = mapped_column(BigInteger, default=0)

    subscriptions: Mapped[list[Subscription]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )
