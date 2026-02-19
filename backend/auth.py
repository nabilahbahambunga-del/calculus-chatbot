from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import secrets
from email_utils import send_verification_email

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ========================
# PASSWORD FUNCTIONS
# ========================

def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# ========================
# SCHEMAS
# ========================

class RegisterRequest(BaseModel):
    student_id: str
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    student_id: str
    password: str


# ========================
# REGISTER
# ========================

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        (User.student_id == data.student_id) |
        (User.email == data.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    token = secrets.token_urlsafe(32)

    new_user = User(
        student_id=data.student_id,
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        verification_token=token
    )

    db.add(new_user)
    db.commit()

    send_verification_email(data.email, token)

    return {"message": "Registered successfully. Please verify your email."}

# ========================
# VERIFY EMAIL
# ========================

@router.get("/verify/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")

    user.is_verified = True
    user.verification_token = None
    db.commit()

    return {"message": "Email verified successfully"}


# ========================
# LOGIN
# ========================

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.student_id == data.student_id).first()

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email first")

    return {
        "message": "Login successful",
        "user_id": user.id,
        "role": user.role
    }

@router.get("/verify/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")

    user.is_verified = True
    user.verification_token = None
    db.commit()

    return {"message": "Email verified successfully"}
