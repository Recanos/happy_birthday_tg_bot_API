from datetime import datetime
from pydantic import BaseModel


class UserBaseSchema(BaseModel):
    name: str
    telegram_id: int

    class Config:
        orm_mode = True


class SubscriptionBaseSchema(BaseModel):
    subscriber_id: int
    subscribed_to_id: int

    class Config:
        orm_mode = True


class UserCreateSchema(UserBaseSchema):
    date_of_birth: datetime


class UserSchema(UserBaseSchema):
    id: int
    date_of_birth: datetime
    subscribers: list[SubscriptionBaseSchema] = []
    subscriptions: list[SubscriptionBaseSchema] = []


class SubscriptionSchema(SubscriptionBaseSchema):
    subscriber: UserBaseSchema
    subscribed_to: UserBaseSchema
