from jwt import decode
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from task_tracker.domain import model
from task_tracker.config import settings
from task_tracker.service_layer.unit_of_work import get_unit_of_work
from task_tracker.service_layer import user as user_service


router = APIRouter()
security = HTTPBearer()


async def get_user(
    authorization: HTTPAuthorizationCredentials = Depends(security),
) -> model.User:
    try:
        token = authorization.credentials
        token_data = decode(token, settings.auth_secret, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=403)

    public_id = token_data.get("public_id")
    if not public_id:
        raise HTTPException(status_code=403)

    uow = await get_unit_of_work()
    async with uow:
        user = await user_service.get_user_by_public_id(uow, public_id)

    if not user:
        raise HTTPException(status_code=403)

    return user


@router.get("/whoami", response_model=model.User)
async def get_whoami(user: model.User = Depends(get_user)):
    return user
