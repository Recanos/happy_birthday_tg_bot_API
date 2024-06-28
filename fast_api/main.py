<<<<<<< HEAD
from fastapi import FastAPI, HTTPException, Depends, status, Body
from sqlalchemy.orm import Session
from typing import List, Annotated, Optional
from .models import Base
from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Happy Birthday!",
    description="API для управления пользователями и подписками на дни рождения с использованием FastAPI и SQLAlchemy",
    openapi_tags=[
        {"name": "Users", "description": "Маршруты для управления пользователями"},
        {"name": "Subscriptions", "description": "Маршруты для управления подписками"},
    ]
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/employees/", response_model=schemas.UserSchema, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user: schemas.UserCreateSchema, db: Session = Depends(get_db)):
    """
    Создание нового пользователя
    """
    db_user = crud.get_user_by_telegram_id(db, telegram_id=user.telegram_id)
    if db_user:
        raise HTTPException(status_code=400, detail="Employee with this Telegram ID already registered")
    return crud.create_user(db=db, user=user)


@app.get("/get_employees", response_model=List[schemas.UserSchema], tags=["Users"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получение списка пользователей
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/check_happy_birthday", response_model=List[schemas.UserSchema], tags=["Users"])
def read_users_with_happy_birthday(telegram_id: Optional[int | None] = None, skip: int = 0, limit: int = 100,
                                   db: Session = Depends(get_db)):
    """
    Получение списка пользователей, у которых сегодня день рождения
    """
    users = crud.get_users_with_happy_birthday(db, telegram_id=telegram_id, skip=skip, limit=limit)
    return users


@app.get("/employee/{user_telegram_id}", response_model=schemas.UserSchema, tags=["Users"])
def read_user(user_telegram_id: int, db: Session = Depends(get_db)):
    """
    Получение подробной информации о пользователе
    """
    db_user = crud.get_user_by_telegram_id(db, telegram_id=user_telegram_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_user


@app.post("/subscribe/{subscribed_to_telegram_id}", response_model=schemas.SubscriptionSchema,
          status_code=status.HTTP_201_CREATED, tags=["Subscriptions"])
def create_subscription_for_user(
        subscribed_to_telegram_id: int, subscriber_telegram_id: Annotated[int, Body()], db: Session = Depends(get_db)
):
    """
    Подписка на пользователя. В теле указать telegram_id того, кто подписывается. В пути - на кого
    """
    try:
        return crud.create_user_subscription(
            db=db,
            subscribed_to_telegram_id=subscribed_to_telegram_id,
            subscriber_telegram_id=subscriber_telegram_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/subscribe_all", response_model=List[schemas.SubscriptionSchema], tags=["Subscriptions"])
def subscribe_to_all_users(user_telegram_id: Annotated[int, Body()], db: Session = Depends(get_db)):
    """
    Подписка на всех пользователей. В теле указать telegram_id того, кто подписывается
    """
    try:
        subscriptions = crud.subscribe_to_all(db, user_telegram_id)
        return subscriptions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/unsubscribe_all", tags=["Subscriptions"])
def unsubscribe_from_all_users(user_telegram_id: Annotated[int, Body()], db: Session = Depends(get_db)):
    """
    Отписка от всех пользователей. В теле указать telegram_id того, кто отписывается
    """
    try:
        subscriptions = crud.unsubscribe_all(db, user_telegram_id)
        return subscriptions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/unsubscribe/{subscribed_to_telegram_id}",
            tags=["Subscriptions"])
def unsubscribe_from_user(
        subscribed_to_telegram_id: int, subscriber_telegram_id: Annotated[int, Body()], db: Session = Depends(get_db)
):
    """
    Отписка от пользователя. В теле указать telegram_id того, кто отписывается. В пути - от кого
    """
    try:
        return crud.unsubscribe_from_user(db, subscriber_telegram_id, subscribed_to_telegram_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/subscriptions/", response_model=List[schemas.SubscriptionSchema], tags=["Subscriptions"])
def read_subscriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получение списка подписок
    """
    subscriptions = crud.get_subscriptions(db, skip=skip, limit=limit)
    return subscriptions


@app.delete("/delete_employee/{telegram_id}", tags=["Users"])
def delete_staff(telegram_id: int, db: Session = Depends(get_db)):
    """
    Удаление пользователя
    """
    try:
        return crud.delete_user(db, telegram_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
=======
from fastapi import FastAPI, HTTPException, Depends, status, Body
from sqlalchemy.orm import Session
from typing import List, Annotated, Optional
from .models import Base
from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Happy Birthday!",
    description="API для управления пользователями и подписками на дни рождения с использованием FastAPI и SQLAlchemy",
    openapi_tags=[
        {"name": "Users", "description": "Маршруты для управления пользователями"},
        {"name": "Subscriptions", "description": "Маршруты для управления подписками"},
    ]
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/employees/", response_model=schemas.UserSchema, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user: schemas.UserCreateSchema, db: Session = Depends(get_db)):
    """
    Создание нового пользователя
    """
    db_user = crud.get_user_by_telegram_id(db, telegram_id=user.telegram_id)
    if db_user:
        raise HTTPException(status_code=400, detail="Employee with this Telegram ID already registered")
    return crud.create_user(db=db, user=user)


@app.get("/get_employees", response_model=List[schemas.UserSchema], tags=["Users"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получение списка пользователей
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/check_happy_birthday", response_model=List[schemas.UserSchema], tags=["Users"])
def read_users_with_happy_birthday(telegram_id: Optional[int | None] = None, skip: int = 0, limit: int = 100,
                                   db: Session = Depends(get_db)):
    """
    Получение списка пользователей, у которых сегодня день рождения
    """
    users = crud.get_users_with_happy_birthday(db, telegram_id=telegram_id, skip=skip, limit=limit)
    return users


@app.get("/employee/{user_telegram_id}", response_model=schemas.UserSchema, tags=["Users"])
def read_user(user_telegram_id: int, db: Session = Depends(get_db)):
    """
    Получение подробной информации о пользователе
    """
    db_user = crud.get_user_by_telegram_id(db, telegram_id=user_telegram_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_user


@app.post("/subscribe/{subscribed_to_telegram_id}", response_model=schemas.SubscriptionSchema,
          status_code=status.HTTP_201_CREATED, tags=["Subscriptions"])
def create_subscription_for_user(
        subscribed_to_telegram_id: int, subscriber_telegram_id: Annotated[int, Body()], db: Session = Depends(get_db)
):
    """
    Подписка на пользователя. В теле указать telegram_id того, кто подписывается. В пути - на кого
    """
    try:
        return crud.create_user_subscription(
            db=db,
            subscribed_to_telegram_id=subscribed_to_telegram_id,
            subscriber_telegram_id=subscriber_telegram_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/subscribe_all", response_model=List[schemas.SubscriptionSchema], tags=["Subscriptions"])
def subscribe_to_all_users(user_telegram_id: Annotated[int, Body()], db: Session = Depends(get_db)):
    """
    Подписка на всех пользователей. В теле указать telegram_id того, кто подписывается
    """
    try:
        subscriptions = crud.subscribe_to_all(db, user_telegram_id)
        return subscriptions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/unsubscribe_all", tags=["Subscriptions"])
def unsubscribe_from_all_users(user_telegram_id: Annotated[int, Body()], db: Session = Depends(get_db)):
    """
    Отписка от всех пользователей. В теле указать telegram_id того, кто отписывается
    """
    try:
        subscriptions = crud.unsubscribe_all(db, user_telegram_id)
        return subscriptions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/unsubscribe/{subscribed_to_telegram_id}",
            tags=["Subscriptions"])
def unsubscribe_from_user(
        subscribed_to_telegram_id: int, subscriber_telegram_id: Annotated[int, Body()], db: Session = Depends(get_db)
):
    """
    Отписка от пользователя. В теле указать telegram_id того, кто отписывается. В пути - от кого
    """
    try:
        return crud.unsubscribe_from_user(db, subscriber_telegram_id, subscribed_to_telegram_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/subscriptions/", response_model=List[schemas.SubscriptionSchema], tags=["Subscriptions"])
def read_subscriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получение списка подписок
    """
    subscriptions = crud.get_subscriptions(db, skip=skip, limit=limit)
    return subscriptions


@app.delete("/delete_employee/{telegram_id}", tags=["Users"])
def delete_staff(telegram_id: int, db: Session = Depends(get_db)):
    """
    Удаление пользователя
    """
    try:
        return crud.delete_user(db, telegram_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
>>>>>>> 523e111b3b7e89f078dd8941e429c20216035a24
