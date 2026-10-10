from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, Token, User, LoginRequest
from app.services.auth_service import AuthService
from app.models.user import User as UserModel

router = APIRouter()

@router.post("/register", response_model=User)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(UserModel).filter(
        (UserModel.username == user.username) | (UserModel.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    return AuthService.create_user(db, user)

@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = AuthService.create_access_token_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}