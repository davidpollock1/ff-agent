from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from app.auth.schemas import TokenData
from app.models.user import User
from sqlmodel import Session, select
from app.core.settings import settings


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class AuthConfig:
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


class AuthService:
    def __init__(
        self,
        config: AuthConfig,
        *,
        password_hasher: PasswordHash | None = None,
        now: Callable[[], datetime] = utcnow,
    ) -> None:
        self._config = config
        self._hasher = password_hasher or PasswordHash.recommended()
        self._now = now

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self._hasher.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self._hasher.hash(password)

    def get_user(self, session: Session, id: str) -> User | None:
        return session.exec(select(User).where(User.id == id)).first()

    def get_user_by_email(self, session: Session, email: str) -> User | None:
        return session.exec(select(User).where(User.email == email)).first()

    def authenticate_user(
        self, session: Session, username: str, password: str
    ) -> User | None:
        user = self.get_user_by_email(session, username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, *, sub: str, expires_minutes: int) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": sub,
            "iat": now,
            "exp": now + timedelta(minutes=expires_minutes),
        }
        return jwt.encode(
            payload, self._config.secret_key, algorithm=self._config.algorithm
        )

    def decode_token(self, token: str) -> TokenData:
        try:
            payload = jwt.decode(
                token,
                self._config.secret_key,
                algorithms=[self._config.algorithm],
            )
        except InvalidTokenError as e:
            raise ValueError("invalid_token") from e

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("missing_sub")

        return TokenData(sub=user_id)


auth_service = AuthService(
    AuthConfig(
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
    )
)
