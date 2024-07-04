from typing_extensions import List, Optional, Annotated

from . import schemas, crud
from . import models
from database import get_async_session
import os
import sys
from fastapi import FastAPI, Body
from fastapi_cache.decorator import cache

sys.path.append(os.path.join(sys.path[0], 'src'))

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/api"
)


@router.post("/employees/", response_model=schemas.UserSchema, status_code=status.HTTP_201_CREATED, tags=["Users"])
async def create_user(user: schemas.UserCreateSchema, session: AsyncSession = Depends(get_async_session)):
    """
    Создание нового пользователя
    """
    db_user = await crud.get_user_by_telegram_id(session, telegram_id=user.telegram_id)
    if db_user:
        raise HTTPException(status_code=400, detail="Employee with this Telegram ID already registered")
    return await crud.create_user(session=session, user=user)  # Добавлен await


@router.get("/get_employees", response_model=List[schemas.UserSchema], tags=["Users"])
@cache(expire=30)
async def read_users(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_async_session)):
    """
    Получение списка пользователей
    """
    users = await crud.get_users(session, skip=skip, limit=limit)
    return users


@router.get("/check_happy_birthday", response_model=List[schemas.UserSchema], tags=["Users"])
@cache(expire=15)
async def read_users_with_happy_birthday(telegram_id: Optional[int | None] = None, skip: int = 0, limit: int = 100,
                                         session: AsyncSession = Depends(get_async_session)):
    """
    Получение списка пользователей, у которых сегодня день рождения
    """
    users = await crud.get_users_with_happy_birthday(session, telegram_id=telegram_id, skip=skip,
                                                     limit=limit)
    return users


@router.get("/employee/{user_telegram_id}", response_model=schemas.UserSchema, tags=["Users"])
async def read_user(user_telegram_id: int, session: AsyncSession = Depends(get_async_session)):
    """
    Получение подробной информации о пользователе
    """
    db_user = await crud.get_user_by_telegram_id(session, telegram_id=user_telegram_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_user


@router.post("/subscribe/{subscribed_to_telegram_id}", response_model=schemas.SubscriptionSchema,
             status_code=status.HTTP_201_CREATED, tags=["Subscriptions"])
async def create_subscription_for_user(
        subscribed_to_telegram_id: int, subscriber_telegram_id: Annotated[int, Body()],
        session: AsyncSession = Depends(get_async_session)
):
    """
    Подписка на пользователя. В теле указать telegram_id того, кто подписывается. В пути - на кого
    """
    try:
        return await crud.create_user_subscription(
            session=session,
            subscribed_to_telegram_id=subscribed_to_telegram_id,
            subscriber_telegram_id=subscriber_telegram_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/subscribe_all", response_model=List[schemas.SubscriptionSchema], tags=["Subscriptions"])
async def subscribe_to_all_users(user_telegram_id: Annotated[int, Body()],
                                 session: AsyncSession = Depends(get_async_session)):
    """
    Подписка на всех пользователей. В теле указать telegram_id того, кто подписывается
    """
    try:
        subscriptions = await crud.subscribe_to_all(session, user_telegram_id)
        return subscriptions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/unsubscribe_all", response_model=str, tags=["Subscriptions"])
async def unsubscribe_from_all_users(user_telegram_id: Annotated[int, Body()],
                                     session: AsyncSession = Depends(get_async_session)):
    """
    Отписка от всех пользователей. В теле указать telegram_id того, кто отписывается
    """
    try:
        subscriptions = await crud.unsubscribe_all(session, user_telegram_id)
        return subscriptions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/unsubscribe/{subscribed_to_telegram_id}", response_model=str,
               tags=["Subscriptions"])
async def unsubscribe_from_user(
        subscribed_to_telegram_id: int, subscriber_telegram_id: Annotated[int, Body()],
        session: AsyncSession = Depends(get_async_session)
):
    """
    Отписка от пользователя. В теле указать telegram_id того, кто отписывается. В пути - от кого
    """
    try:
        return await crud.unsubscribe_from_user(session, subscriber_telegram_id,
                                                subscribed_to_telegram_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subscriptions/", response_model=List[schemas.SubscriptionSchema], tags=["Subscriptions"])
@cache(expire=30)
async def read_subscriptions(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_async_session)):
    """
    Получение списка подписок
    """
    subscriptions = await crud.get_subscriptions(session, skip=skip, limit=limit)
    return subscriptions


@router.delete("/delete_employee/{telegram_id}", response_model=schemas.UserSchema, tags=["Users"])
async def delete_staff(telegram_id: int, session: AsyncSession = Depends(get_async_session)):
    """
    Удаление пользователя
    """
    try:
        return await crud.delete_user(session, telegram_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
