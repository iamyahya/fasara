from datetime import datetime

from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.schemas import SignUp
from app.db import Model as _
from app.models import User, Invite
from app.models.user import UserSecurity


router = APIRouter()


@router.post("/sign-up")
async def route_sign_up(form: SignUp):
    invite = await Invite(code=form.code).one()
    if invite is None or invite.created_at > datetime.utcnow():
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["body", "code"],
                    "msg": "Invite not found",
                    "type": "value_error.not_exist"
                }
            ]
        )
    if invite.to_id:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["body", "code"],
                    "msg": "Invite already used",
                    "type": "value_error.used"
                }
            ]
        )
    # TODO: Test next logic
    if await User(username=form.username).count():
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["body", "username"],
                    "msg": "Username already used",
                    "type": "value_error.exist"
                }
            ]
        )
    user = User(
        username=form.username,
        hashed_password=UserSecurity.to_hash(form.password),
        invites=[
            # Schedule adding new Invite for User(id=from_id)
            Invite(
                created_at=datetime.utcnow() + settings.invite_delta
            )
        ]
    )
    await user.save()
    invite.to_id = user.id
    await invite.save()
    await invite.clone()
    ctrl = UserSecurity(username=form.username, password=form.password)
    if not await ctrl.authenticate():
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["body", "password"],
                    "msg": "Incorrect username or password",
                    "type": "value_error.compare"
                }
            ]
        )
    return {"access_token": ctrl.access_token, "token_type": "bearer"}


@router.post("/sign-in")
async def route_sign_in(
    form: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(_.get_session)
):
    ctrl = UserSecurity(**form.__dict__)
    if not await ctrl.authenticate():
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["body", "password"],
                    "msg": "Incorrect username or password",
                    "type": "value_error.compare"
                }
            ]
        )
    return {"access_token": ctrl.access_token, "token_type": "bearer"}


@router.get("/token")
async def route_sync_token(
    user: User = Depends(UserSecurity.get_me),
):
    ctrl = UserSecurity(None, "")
    ctrl.user = user
    return {"access_token": ctrl.access_token, "token_type": "bearer"}
