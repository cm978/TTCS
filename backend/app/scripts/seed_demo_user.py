import os

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.schemas.auth import RegisterRequest
from app.services.auth_service import AuthService, DuplicateEmailError


def main() -> None:
    Base.metadata.create_all(bind=engine)
    email = os.getenv("DEMO_USER_EMAIL", "demo@example.com")
    password = os.getenv("DEMO_USER_PASSWORD", "DemoPass123!")
    display_name = os.getenv("DEMO_USER_DISPLAY_NAME", "TTCS Demo User")

    with SessionLocal() as db:
        service = AuthService(db)
        try:
            service.register(RegisterRequest(email=email, password=password, display_name=display_name))
            print(f"Created local demo user: {email}")
        except DuplicateEmailError:
            print(f"Local demo user already exists: {email}")


if __name__ == "__main__":
    main()
