from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .inbound import Inbound


class Domain(Base, TimestampMixin):
    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(253), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    inbounds: Mapped[list[Inbound]] = relationship(back_populates="domain")
