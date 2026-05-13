from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from .enum import PortType, ProtocolType

if TYPE_CHECKING:
    from .domain import Domain
    from .subscription_inbound import SubscriptionInbound


class Inbound(Base, TimestampMixin):
    __tablename__ = "inbounds"

    id: Mapped[int] = mapped_column(primary_key=True)
    protocol: Mapped[ProtocolType] = mapped_column(SAEnum(ProtocolType), nullable=False)
    port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    port_type: Mapped[PortType] = mapped_column(
        SAEnum(PortType), default=PortType.RANDOM
    )
    sni: Mapped[str | None] = mapped_column(String(253), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    domain_id: Mapped[int | None] = mapped_column(
        ForeignKey("domains.id", ondelete="SET NULL"), nullable=True
    )

    domain: Mapped[Domain] = relationship(back_populates="inbounds")
    subscription_inbounds: Mapped[list[SubscriptionInbound]] = relationship(
        back_populates="inbound"
    )
