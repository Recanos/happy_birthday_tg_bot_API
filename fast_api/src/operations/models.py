from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Subscription(Base):
    __tablename__ = 'subscriptions'

    id: Mapped[int] = mapped_column(primary_key=True)
    subscriber_id: Mapped[int] = mapped_column(ForeignKey('users.telegram_id'))
    subscribed_to_id: Mapped[int] = mapped_column(ForeignKey('users.telegram_id'))

    subscriber: Mapped["User"] = relationship(foreign_keys=[subscriber_id], back_populates="subscriptions", lazy="selectin")
    subscribed_to: Mapped["User"] = relationship(foreign_keys=[subscribed_to_id], back_populates="subscribed_by", lazy="selectin")


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    date_of_birth: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    subscribers: Mapped[list["Subscription"]] = relationship(
        'Subscription',
        foreign_keys=[Subscription.subscribed_to_id],
        back_populates="subscribed_to",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    subscribed_by: Mapped[list["Subscription"]] = relationship(
        'Subscription',
        foreign_keys=[Subscription.subscriber_id],
        back_populates="subscriber",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    subscriptions: Mapped[list["Subscription"]] = relationship(
        'Subscription',
        foreign_keys=[Subscription.subscriber_id],
        back_populates="subscriber",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
