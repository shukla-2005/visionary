from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.auth import get_password_hash, verify_password, create_access_token
from datetime import timedelta

class AuthService:
    @staticmethod
    def create_user(db: Session, user: UserCreate):
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user

    @staticmethod
    def create_access_token_for_user(user: User):
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return access_token