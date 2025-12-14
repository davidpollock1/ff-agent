from typing import Annotated
from app.deps import SessionDep, CurrentUserDep

from sqlmodel import select
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.schemas import Token, UserRead, UserCreate
from app.models.user import User
from app.auth.service import auth_service
from app.core.settings import settings

router = APIRouter(prefix="/auth", tags=["users"])


@router.post("/signup", response_model=UserRead, status_code=201)
def signup(payload: UserCreate, session: SessionDep) -> UserRead:
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=auth_service.get_password_hash(payload.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return UserRead(id=user.id, email=user.email)


@router.post("/token")
async def login_for_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = auth_service.authenticate_user(
        session, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(
        sub=str(user.id),
        expires_minutes=settings.access_token_expire_minutes,
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me", response_model=UserRead)
async def read_users_me(current_user: CurrentUserDep) -> UserRead:
    return UserRead(id=current_user.id, email=current_user.email)
