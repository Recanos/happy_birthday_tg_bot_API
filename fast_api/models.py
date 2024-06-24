from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from .database import Base


# Создайте модель для связующей таблицы
class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    subscriber_id = Column(Integer, ForeignKey('users.telegram_id'))
    subscribed_to_id = Column(Integer, ForeignKey('users.telegram_id'))

    # Определяем отношения с User, используя back_populates для автоматического подтягивания связанных данных
    subscriber = relationship("User", foreign_keys=[subscriber_id], back_populates="subscriptions")
    subscribed_to = relationship("User", foreign_keys=[subscribed_to_id], back_populates="subscribed_by")


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    telegram_id = Column(Integer, unique=True, nullable=False)
    date_of_birth = Column(TIMESTAMP(timezone=True), nullable=False)

    subscribers = relationship(
        'Subscription',
        foreign_keys=[Subscription.subscribed_to_id],
        back_populates="subscribed_to",
        cascade="all, delete-orphan"
    )

    subscribed_by = relationship(
        'Subscription',
        foreign_keys=[Subscription.subscriber_id],
        back_populates="subscriber",
        cascade="all, delete-orphan"
    )

    subscriptions = relationship(
        'Subscription',
        foreign_keys=[Subscription.subscriber_id],
        back_populates="subscriber",
        cascade="all, delete-orphan"
    )

