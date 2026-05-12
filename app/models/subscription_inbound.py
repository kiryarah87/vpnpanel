from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .subscription import Subscription
from .inbound import Inbound


class SubscriptionInbound(Base):
    """Many-to-many: Subscription <-> Inbound"""

    __tablename__ = "subscription_inbounds"
    __table_args__ = (UniqueConstraint("subscription_id", "inbound_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    subscription_id: Mapped[int] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False
    )
    inbound_id: Mapped[int] = mapped_column(
        ForeignKey("inbounds.id", ondelete="CASCADE"), nullable=False
    )

    subscription: Mapped["Subscription"] = relationship(
        back_populates="subscription_inbounds"
    )
    inbound: Mapped["Inbound"] = relationship(back_populates="subscription_inbounds")
