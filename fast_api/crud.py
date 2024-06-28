<<<<<<< HEAD
from datetime import datetime
from sqlalchemy import extract, select, delete, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException
from sqlalchemy import select


def create_user(db: Session, user: schemas.UserCreateSchema) -> models.User:
    db_user = models.User(name=user.name, telegram_id=user.telegram_id, date_of_birth=user.date_of_birth)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_telegram_name(db: Session, user_telegram_name: str) -> models.User:
    stmt = select(models.User).where(models.User.name == user_telegram_name)
    result = db.execute(stmt).scalar_one_or_none()
    return result


def get_user_by_telegram_id(db: Session, telegram_id: int) -> models.User:
    stmt = select(models.User).where(models.User.telegram_id == telegram_id)
    result = db.execute(stmt).scalar_one_or_none()
    return result


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    stmt = select(models.User).offset(skip).limit(limit)
    result = db.execute(stmt).scalars().all()
    return result


def get_users_with_happy_birthday(db: Session, telegram_id: int | None = None, skip: int = 0, limit: int = 100) -> list[
    models.User]:
    today = datetime.utcnow()

    stmt = select(models.User).where(
        extract('day', models.User.date_of_birth) == today.day,
        extract('month', models.User.date_of_birth) == today.month
    )

    if telegram_id is not None:
        subquery = select(models.Subscription.subscribed_to_id).where(
            models.Subscription.subscriber_id == telegram_id).subquery()

        stmt = stmt.where(models.User.telegram_id.in_(subquery))

    stmt = stmt.offset(skip).limit(limit)
    result = db.execute(stmt).scalars().all()
    return result


def create_user_subscription(db: Session, subscribed_to_telegram_id: int,
                             subscriber_telegram_id: int) -> models.Subscription:
    stmt_user_check = select(models.User).where(
        models.User.telegram_id.in_([subscriber_telegram_id, subscribed_to_telegram_id])
    )
    users = db.execute(stmt_user_check).scalars().all()

    if len(users) != 2:
        raise HTTPException(status_code=400, detail="Subscriber or subscribed employee not found")

    subscriber = next(user for user in users if user.telegram_id == subscriber_telegram_id)
    subscribed_to = next(user for user in users if user.telegram_id == subscribed_to_telegram_id)

    if subscriber == subscribed_to:
        raise HTTPException(status_code=400, detail="Unable to follow yourself")

    # Подзапрос для проверки на уже существующую подписку
    stmt_sub_check = select(models.Subscription).where(
        models.Subscription.subscriber_id == subscriber_telegram_id,
        models.Subscription.subscribed_to_id == subscribed_to_telegram_id
    )
    sub_repeat = db.execute(stmt_sub_check).scalars().first()

    if sub_repeat:
        raise HTTPException(status_code=400, detail="Already subscribed")

    # Создание новой подписки внутри транзакции
    db_subscription = models.Subscription(
        subscriber_id=subscriber.telegram_id,
        subscribed_to_id=subscribed_to.telegram_id
    )

    try:
        db.add(db_subscription)
        db.commit()
        db.refresh(db_subscription)
    except:
        db.rollback()
        raise

    return db_subscription


def subscribe_to_all(db: Session, user_telegram_id: int):
    user_stmt = select(models.User).where(models.User.telegram_id == user_telegram_id)
    user = db.execute(user_stmt).scalars().first()
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
    all_users_except_current = db.execute(new_users_stmt).scalars().all()

    if not all_users_except_current:
        raise HTTPException(status_code=400, detail="Nothing to subscribe")

    subscriptions = [
        models.Subscription(
            subscriber_id=user.telegram_id,
            subscribed_to_id=other_user.telegram_id
        ) for other_user in all_users_except_current
    ]

    db.bulk_save_objects(subscriptions)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="There was an error committing the subscriptions to the database")
    return db.query(models.Subscription).filter(models.Subscription.subscriber_id == user.telegram_id).all()


def unsubscribe_all(db: Session, user_telegram_id: int):
    user_stmt = select(models.User).where(models.User.telegram_id == user_telegram_id)
    user = db.execute(user_stmt).scalars().first()
    if not user:
        raise HTTPException(status_code=400, detail="Employee not found")

    sub_del_stmt = delete(models.Subscription).where(
        models.Subscription.subscriber_id == user.telegram_id
    )

    result = db.execute(sub_del_stmt)

    if result.rowcount > 0:
        db.commit()
        return f"Unsubscribed from {result.rowcount} users."
    else:
        db.rollback()
        raise HTTPException(status_code=400, detail="No one to unsubscribe from")

def unsubscribe_from_user(db: Session, subscriber_telegram_id: int, subscribed_to_telegram_id: int):

    users_stmt = select(models.User).where(
        models.User.telegram_id.in_([subscriber_telegram_id, subscribed_to_telegram_id]))
    users = db.execute(users_stmt).scalars().all()

    if len(users) != 2:
        raise HTTPException(status_code=400, detail="Subscriber or subscribed employee not found")

    sub_del_stmt = delete(models.Subscription).where(
        models.Subscription.subscriber_id == subscriber_telegram_id,
        models.Subscription.subscribed_to_id == subscribed_to_telegram_id
    )

    result = db.execute(sub_del_stmt)

    if result.rowcount > 0:
        db.commit()
        return f"Unsubscribed from user with Telegram ID {subscribed_to_telegram_id}."
    else:
        db.rollback()
        raise HTTPException(status_code=400, detail="No such subscription")
def get_subscriptions(db: Session, skip: int = 0, limit: int = 100) -> list[models.Subscription]:
    stmt = select(models.Subscription).offset(skip).limit(limit).all()
    result = db.execute(stmt).scalars().all()
    return result


def delete_user(db: Session, telegram_id: int):
    db_user = db.query(models.User).filter(models.User.telegram_id == telegram_id).first()
    if db_user:
        user_data = {
            "id": db_user.id,
            "telegram_id": db_user.telegram_id,
            "name": db_user.name,
        }
        db.delete(db_user)
        db.commit()
        return user_data
    raise HTTPException(status_code=400, detail="Employee not found")
=======
from datetime import datetime
from sqlalchemy import extract, select, delete, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException
from sqlalchemy import select


def create_user(db: Session, user: schemas.UserCreateSchema) -> models.User:
    db_user = models.User(name=user.name, telegram_id=user.telegram_id, date_of_birth=user.date_of_birth)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_telegram_name(db: Session, user_telegram_name: str) -> models.User:
    stmt = select(models.User).where(models.User.name == user_telegram_name)
    result = db.execute(stmt).scalar_one_or_none()
    return result


def get_user_by_telegram_id(db: Session, telegram_id: int) -> models.User:
    stmt = select(models.User).where(models.User.telegram_id == telegram_id)
    result = db.execute(stmt).scalar_one_or_none()
    return result


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    stmt = select(models.User).offset(skip).limit(limit)
    result = db.execute(stmt).scalars().all()
    return result


def get_users_with_happy_birthday(db: Session, telegram_id: int | None = None, skip: int = 0, limit: int = 100) -> list[
    models.User]:
    today = datetime.utcnow()

    stmt = select(models.User).where(
        extract('day', models.User.date_of_birth) == today.day,
        extract('month', models.User.date_of_birth) == today.month
    )

    if telegram_id is not None:
        subquery = select(models.Subscription.subscribed_to_id).where(
            models.Subscription.subscriber_id == telegram_id).subquery()

        stmt = stmt.where(models.User.telegram_id.in_(subquery))

    stmt = stmt.offset(skip).limit(limit)
    result = db.execute(stmt).scalars().all()
    return result


def create_user_subscription(db: Session, subscribed_to_telegram_id: int,
                             subscriber_telegram_id: int) -> models.Subscription:
    stmt_user_check = select(models.User).where(
        models.User.telegram_id.in_([subscriber_telegram_id, subscribed_to_telegram_id])
    )
    users = db.execute(stmt_user_check).scalars().all()

    if len(users) != 2:
        raise HTTPException(status_code=400, detail="Subscriber or subscribed employee not found")

    subscriber = next(user for user in users if user.telegram_id == subscriber_telegram_id)
    subscribed_to = next(user for user in users if user.telegram_id == subscribed_to_telegram_id)

    if subscriber == subscribed_to:
        raise HTTPException(status_code=400, detail="Unable to follow yourself")

    # Подзапрос для проверки на уже существующую подписку
    stmt_sub_check = select(models.Subscription).where(
        models.Subscription.subscriber_id == subscriber_telegram_id,
        models.Subscription.subscribed_to_id == subscribed_to_telegram_id
    )
    sub_repeat = db.execute(stmt_sub_check).scalars().first()

    if sub_repeat:
        raise HTTPException(status_code=400, detail="Already subscribed")

    # Создание новой подписки внутри транзакции
    db_subscription = models.Subscription(
        subscriber_id=subscriber.telegram_id,
        subscribed_to_id=subscribed_to.telegram_id
    )

    try:
        db.add(db_subscription)
        db.commit()
        db.refresh(db_subscription)
    except:
        db.rollback()
        raise

    return db_subscription


def subscribe_to_all(db: Session, user_telegram_id: int):
    user_stmt = select(models.User).where(models.User.telegram_id == user_telegram_id)
    user = db.execute(user_stmt).scalars().first()
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
    all_users_except_current = db.execute(new_users_stmt).scalars().all()

    if not all_users_except_current:
        raise HTTPException(status_code=400, detail="Nothing to subscribe")

    subscriptions = [
        models.Subscription(
            subscriber_id=user.telegram_id,
            subscribed_to_id=other_user.telegram_id
        ) for other_user in all_users_except_current
    ]

    db.bulk_save_objects(subscriptions)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="There was an error committing the subscriptions to the database")
    return db.query(models.Subscription).filter(models.Subscription.subscriber_id == user.telegram_id).all()


def unsubscribe_all(db: Session, user_telegram_id: int):
    user_stmt = select(models.User).where(models.User.telegram_id == user_telegram_id)
    user = db.execute(user_stmt).scalars().first()
    if not user:
        raise HTTPException(status_code=400, detail="Employee not found")

    sub_del_stmt = delete(models.Subscription).where(
        models.Subscription.subscriber_id == user.telegram_id
    )

    result = db.execute(sub_del_stmt)

    if result.rowcount > 0:
        db.commit()
        return f"Unsubscribed from {result.rowcount} users."
    else:
        db.rollback()
        raise HTTPException(status_code=400, detail="No one to unsubscribe from")

def unsubscribe_from_user(db: Session, subscriber_telegram_id: int, subscribed_to_telegram_id: int):

    users_stmt = select(models.User).where(
        models.User.telegram_id.in_([subscriber_telegram_id, subscribed_to_telegram_id]))
    users = db.execute(users_stmt).scalars().all()

    if len(users) != 2:
        raise HTTPException(status_code=400, detail="Subscriber or subscribed employee not found")

    sub_del_stmt = delete(models.Subscription).where(
        models.Subscription.subscriber_id == subscriber_telegram_id,
        models.Subscription.subscribed_to_id == subscribed_to_telegram_id
    )

    result = db.execute(sub_del_stmt)

    if result.rowcount > 0:
        db.commit()
        return f"Unsubscribed from user with Telegram ID {subscribed_to_telegram_id}."
    else:
        db.rollback()
        raise HTTPException(status_code=400, detail="No such subscription")
def get_subscriptions(db: Session, skip: int = 0, limit: int = 100) -> list[models.Subscription]:
    stmt = select(models.Subscription).offset(skip).limit(limit).all()
    result = db.execute(stmt).scalars().all()
    return result


def delete_user(db: Session, telegram_id: int):
    db_user = db.query(models.User).filter(models.User.telegram_id == telegram_id).first()
    if db_user:
        user_data = {
            "id": db_user.id,
            "telegram_id": db_user.telegram_id,
            "name": db_user.name,
        }
        db.delete(db_user)
        db.commit()
        return user_data
    raise HTTPException(status_code=400, detail="Employee not found")
>>>>>>> 523e111b3b7e89f078dd8941e429c20216035a24
