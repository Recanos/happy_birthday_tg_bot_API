from datetime import datetime
from sqlalchemy import extract
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException


def create_user(db: Session, user: schemas.UserCreateSchema) -> models.User:
    db_user = models.User(name=user.name, telegram_id=user.telegram_id, date_of_birth=user.date_of_birth)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_telegram_name(db: Session, user_telegram_name: str) -> models.User:
    return db.query(models.User).filter(models.User.name == user_telegram_name).first()


def get_user_by_telegram_id(db: Session, telegram_id: int) -> models.User:
    return db.query(models.User).filter(models.User.telegram_id == telegram_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def get_users_with_happy_birthday(db: Session, telegram_id: int | None = None, skip: int = 0, limit: int = 100) -> list[
    models.User]:
    today = datetime.utcnow()

    birthday_query = db.query(models.User).filter(
        extract('day', models.User.date_of_birth) == today.day,
        extract('month', models.User.date_of_birth) == today.month
    )

    if telegram_id is not None:
        # Подзапрос для получения подписок конкретного пользователя
        list_needed_ids = db.query(models.Subscription.subscribed_to_id).filter(
            models.Subscription.subscriber_id == telegram_id
        )

        # Фильтр для получения пользователей, на которых подписан конкретный пользователь
        birthday_query = birthday_query.filter(models.User.telegram_id.in_(list_needed_ids))

    return birthday_query.offset(skip).limit(limit).all()




def create_user_subscription(db: Session, subscribed_to_telegram_id: int,
                             subscriber_telegram_id: int) -> models.Subscription:
    subscriber = db.query(models.User).filter(models.User.telegram_id == subscriber_telegram_id).first()
    subscribed_to = db.query(models.User).filter(
        models.User.telegram_id == subscribed_to_telegram_id).first()

    if not subscriber or not subscribed_to:
        raise HTTPException(status_code=400, detail="Subscriber or subscribed employee not found")

    if subscriber == subscribed_to:
        raise HTTPException(status_code=400, detail="Unable to follow yourself")

    sub_repeat = db.query(models.Subscription).filter(
        models.Subscription.subscriber_id == subscriber_telegram_id).filter(
        models.Subscription.subscribed_to_id == subscribed_to_telegram_id
    ).first()

    if sub_repeat:
        raise HTTPException(status_code=400, detail="Already subscribed")

    db_subscription = models.Subscription(
        subscriber_id=subscriber.telegram_id,
        subscribed_to_id=subscribed_to.telegram_id
    )

    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)

    return db_subscription


def subscribe_to_all(db: Session, user_telegram_id: int):
    user = db.query(models.User).filter(models.User.telegram_id == user_telegram_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Employee not found")

    all_users_except_current = db.query(models.User).filter(models.User.telegram_id != user.telegram_id).all()

    subscriptions = []
    for other_user in all_users_except_current:
        existing_subscription = db.query(models.Subscription).filter(
            models.Subscription.subscriber_id == user.telegram_id,
            models.Subscription.subscribed_to_id == other_user.telegram_id
        ).first()

        if not existing_subscription:
            subscriptions.append(models.Subscription(
                subscriber_id=user.telegram_id,
                subscribed_to_id=other_user.telegram_id
            ))

    if subscriptions:
        db.bulk_save_objects(subscriptions)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400,
                                detail="There was an error committing the subscriptions to the database")

        return db.query(models.Subscription).filter(models.Subscription.subscriber_id == user.telegram_id).all()
    else:
        raise HTTPException(status_code=400, detail="Nothing to subscribe")


def unsubscribe_all(db: Session, user_telegram_id: int):
    user = db.query(models.User).filter(models.User.telegram_id == user_telegram_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Employee not found")

    subscriptions = db.query(models.Subscription).filter(models.Subscription.subscriber_id == user.telegram_id).all()
    if subscriptions:
        for subscription in subscriptions:
            db.delete(subscription)

        db.commit()
        return subscriptions
    else:
        raise HTTPException(status_code=400, detail="No one to unsubscribe from")


def unsubscribe_from_user(db: Session, subscriber_telegram_id: int, subscribed_to_telegram_id: int):
    subscriber = db.query(models.User).filter(models.User.telegram_id == subscriber_telegram_id).first()
    subscribed_to = db.query(models.User).filter(models.User.telegram_id == subscribed_to_telegram_id).first()

    if not subscriber or not subscribed_to:
        raise HTTPException(status_code=400, detail="Subscriber or subscribed employee")

    subscription = db.query(models.Subscription).filter(
        models.Subscription.subscriber_id == subscriber.telegram_id,
        models.Subscription.subscribed_to_id == subscribed_to.telegram_id
    ).first()

    if subscription:
        db.delete(subscription)
        db.commit()

        return subscription
    else:
        raise HTTPException(status_code=400, detail="No such subscription")


def get_subscriptions(db: Session, skip: int = 0, limit: int = 100) -> list[models.Subscription]:
    return db.query(models.Subscription).offset(skip).limit(limit).all()


def delete_user(db: Session, telegram_id: int) -> models.User:
    db_user = db.query(models.User).filter(models.User.telegram_id == telegram_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return db_user
    raise HTTPException(status_code=400, detail="Employee not found")
