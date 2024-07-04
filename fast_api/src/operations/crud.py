from datetime import datetime
from sqlalchemy import extract, delete, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas
from . import models
from fastapi import HTTPException
from sqlalchemy import select


async def create_user(session: AsyncSession, user: schemas.UserCreateSchema) -> models.User:
    db_user = models.User(name=user.name, telegram_id=user.telegram_id, date_of_birth=user.date_of_birth)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def get_user_by_telegram_name(session: AsyncSession, user_telegram_name: str) -> models.User:
    stmt = select(models.User).where(models.User.name == user_telegram_name)
    result = (await session.execute(stmt)).scalar_one_or_none()
    return result


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> models.User:
    stmt = select(models.User).where(models.User.telegram_id == telegram_id)
    result = (await session.execute(stmt)).scalar_one_or_none()
    return result


async def get_users(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[models.User]:
    stmt = select(models.User).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_users_with_happy_birthday(session: AsyncSession, telegram_id: int | None = None, skip: int = 0,
                                        limit: int = 100) -> list[models.User]:
    today = datetime.utcnow()

    stmt = select(models.User).where(
        extract('day', models.User.date_of_birth) == today.day,
        extract('month', models.User.date_of_birth) == today.month
    )

    if telegram_id is not None:
        subquery = select(models.Subscription.subscribed_to_id).where(
            models.Subscription.subscriber_id == telegram_id
        ).subquery()

        stmt = stmt.where(models.User.telegram_id.in_(subquery))

    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_user_subscription(session: AsyncSession, subscribed_to_telegram_id: int,
                                   subscriber_telegram_id: int) -> models.Subscription:
    stmt_user_check = select(models.User).where(
        models.User.telegram_id.in_([subscriber_telegram_id, subscribed_to_telegram_id])
    )
    users = (await session.execute(stmt_user_check)).scalars().all()

    if len(users) != 2:
        raise HTTPException(status_code=400, detail="Subscriber or subscribed employee not found")

    subscriber = next(user for user in users if user.telegram_id == subscriber_telegram_id)
    subscribed_to = next(user for user in users if user.telegram_id == subscribed_to_telegram_id)

    if subscriber == subscribed_to:
        raise HTTPException(status_code=400, detail="Unable to follow yourself")

    stmt_sub_check = select(models.Subscription).where(
        models.Subscription.subscriber_id == subscriber_telegram_id,
        models.Subscription.subscribed_to_id == subscribed_to_telegram_id
    )
    sub_repeat = (await session.execute(stmt_sub_check)).scalars().first()

    if sub_repeat:
        raise HTTPException(status_code=400, detail="Already subscribed")

    db_subscription = models.Subscription(
        subscriber_id=subscriber_telegram_id,
        subscribed_to_id=subscribed_to_telegram_id
    )

    try:
        session.add(db_subscription)
        await session.commit()
        await session.refresh(db_subscription)
    except:
        await session.rollback()
        raise

    return db_subscription


async def subscribe_to_all(session: AsyncSession, user_telegram_id: int) -> list[models.Subscription]:
    user_stmt = select(models.User).where(models.User.telegram_id == user_telegram_id)
    user = (await session.execute(user_stmt)).scalars().first()
    if not user:
        raise HTTPException(status_code=400, detail="Employee not found")

    existing_subs_stmt = select(models.Subscription.subscribed_to_id).where(
        models.Subscription.subscriber_id == user.telegram_id
    ).subquery()

    new_users_stmt = select(models.User).where(
        and_(
            models.User.telegram_id != user.telegram_id,
            models.User.telegram_id.not_in(existing_subs_stmt)
        )
    )
    all_users_except_current = (await session.execute(new_users_stmt)).scalars().all()

    if not all_users_except_current:
        raise HTTPException(status_code=400, detail="Nothing to subscribe")

    subscriptions = [
        models.Subscription(
            subscriber_id=user.telegram_id,
            subscribed_to_id=other_user.telegram_id
        ) for other_user in all_users_except_current
    ]

    session.add_all(subscriptions)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="There was an error committing the subscriptions to the database")
    return (await session.execute(
        select(models.Subscription).where(models.Subscription.subscriber_id == user.telegram_id)
    )).scalars().all()


async def unsubscribe_all(session: AsyncSession, user_telegram_id: int) -> str:
    user_stmt = select(models.User).where(models.User.telegram_id == user_telegram_id)
    user = (await session.execute(user_stmt)).scalars().first()
    if not user:
        raise HTTPException(status_code=400, detail="Employee not found")

    sub_del_stmt = delete(models.Subscription).where(
        models.Subscription.subscriber_id == user.telegram_id
    )
    result = await session.execute(sub_del_stmt)

    if result.rowcount > 0:
        await session.commit()
        return f"Unsubscribed from {result.rowcount} users."
    else:
        await session.rollback()
        raise HTTPException(status_code=400, detail="No one to unsubscribe from")


async def unsubscribe_from_user(session: AsyncSession, subscriber_telegram_id: int,
                                subscribed_to_telegram_id: int) -> str:
    users_stmt = select(models.User).where(
        models.User.telegram_id.in_([subscriber_telegram_id, subscribed_to_telegram_id])
    )
    users = (await session.execute(users_stmt)).scalars().all()

    if len(users) != 2:
        raise HTTPException(status_code=400, detail="Subscriber or subscribed employee not found")

    sub_del_stmt = delete(models.Subscription).where(
        models.Subscription.subscriber_id == subscriber_telegram_id,
        models.Subscription.subscribed_to_id == subscribed_to_telegram_id
    )
    result = await session.execute(sub_del_stmt)

    if result.rowcount > 0:
        await session.commit()
        return f"{subscriber_telegram_id} Unsubscribed from user with Telegram ID {subscribed_to_telegram_id}"
    else:
        await session.rollback()
        raise HTTPException(status_code=400, detail="No such subscription")


async def get_subscriptions(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[models.Subscription]:
    stmt = select(models.Subscription).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def delete_user(session: AsyncSession, telegram_id: int) -> schemas.UserSchema:
    db_user = (await session.execute(
        select(models.User).where(models.User.telegram_id == telegram_id)
    )).scalars().first()
    if db_user:
        user_data = {
            "id": db_user.id,
            "telegram_id": db_user.telegram_id,
            "name": db_user.name,
            "date_of_birth": db_user.date_of_birth,
            "subscribers": db_user.subscribers,
            "subscribed_by": db_user.subscribed_by

        }
        await session.delete(db_user)
        await session.commit()
        return user_data
    raise HTTPException(status_code=400, detail="Employee not found")
