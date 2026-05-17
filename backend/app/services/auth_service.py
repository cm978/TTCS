from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest


class DuplicateEmailError(ValueError):
    pass


class InvalidCredentialsError(ValueError):
    pass


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email.lower()))

    def register(self, payload: RegisterRequest) -> User:
        email = payload.email.lower()
        if self.get_by_email(email):
            raise DuplicateEmailError(email)
        user = User(
            email=email,
            display_name=payload.display_name,
            hashed_password=hash_password(payload.password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, payload: LoginRequest) -> tuple[str, User, int]:
        user = self.get_by_email(payload.email)
        if user is None or not user.is_active or not verify_password(payload.password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")
        token, expires_in = create_access_token(str(user.id), {"email": user.email})
        return token, user, expires_in

