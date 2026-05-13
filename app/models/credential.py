from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .client import Client


class ClientCredential(Base, TimestampMixin):
    """Credentials клиента для всех протоколов"""

    __tablename__ = "client_credentials"
    __table_args__ = (UniqueConstraint("client_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    xray_uuid: Mapped[str] = mapped_column(String(36), nullable=False)
    hysteria2_password: Mapped[str] = mapped_column(String(128), nullable=False)
    naiveproxy_username: Mapped[str] = mapped_column(String(64), nullable=False)
    naiveproxy_password: Mapped[str] = mapped_column(String(128), nullable=False)

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )

    client: Mapped[Client] = relationship(back_populates="credential")
