from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, Optional

from database import get_async_session
from operations import crud
from . import tasks

router = APIRouter(prefix="/send_info_to_email")

@router.get("/")
async def send_email_with_data(telegram_id: Optional[Union[int, None]] = None, skip: int = 0, limit: int = 100,
                               session: AsyncSession = Depends(get_async_session)):
    users = await crud.get_users_with_happy_birthday(session, telegram_id=telegram_id, skip=skip, limit=limit)
    user_data = [{"telegram_id": user.telegram_id, "name": user.name} for user in users]

    tasks.send_email.delay(user_data)
    return {"status": 200, "msg": "Successfully sent"}