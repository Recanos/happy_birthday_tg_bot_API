from datetime import datetime
from pydantic import BaseModel


# Схема для сериализации данных о пользователе
class UserBaseSchema(BaseModel):
    name: str
    telegram_id: int

    class Config:
        orm_mode = True


# Схема для сериализации базовых данных подписки
class SubscriptionBaseSchema(BaseModel):
    subscriber_id: int
    subscribed_to_id: int

    class Config:
        orm_mode = True


# Схема при создании нового пользователя
class UserCreateSchema(UserBaseSchema):
    date_of_birth: datetime


# Схема для ответа с полными данными о пользователе
class UserSchema(UserBaseSchema):
    id: int
    date_of_birth: datetime
    subscribers: list[SubscriptionBaseSchema] = []
    subscriptions: list[SubscriptionBaseSchema] = []


# Схема для ответа с полными данными подписки
class SubscriptionSchema(SubscriptionBaseSchema):
    subscriber: UserBaseSchema
    subscribed_to: UserBaseSchema
