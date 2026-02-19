from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import random
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import os

from database import SessionLocal, engine
from models import Base, User, EmailVerification
from auth import hash_password, verify_password

# ================== APP INIT ==================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# ================== DB ==================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================== EMAIL FUNCTION ==================

def send_email(to_email: str, otp: str):

    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")

    print("========== EMAIL DEBUG ==========")
    print("TO:", to_email)
    print("OTP:", otp)
    print("EMAIL_USER:", EMAIL_USER)
    print("EMAIL_PASS EXISTS:", EMAIL_PASS is not None)
    print("=================================")

    if not EMAIL_USER or not EMAIL_PASS:
        raise Exception("EMAIL_USER or EMAIL_PASS not set in Render")

    msg = MIMEText(f"""
Your verification code is:

{otp}

This code will expire in 5 minutes.
""")

    msg["Subject"] = "Email Verification - AI Tutor"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        print("EMAIL SENT SUCCESSFULLY")
    except Exception as e:
        print("EMAIL ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Email sending failed")

# ================== SEND OTP ==================

@app.post("/send-otp")
def send_otp(data: dict, db: Session = Depends(get_db)):

    student_id = data.get("student_id")
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([student_id, name, email, password]):
        raise HTTPException(status_code=400, detail="Missing fields")

    # เช็ค user ซ้ำ
    existing = db.query(User).filter(
        (User.student_id == student_id) |
        (User.email == email)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    # ลบ OTP เก่า (กัน spam)
    db.query(EmailVerification).filter(
        EmailVerification.email == email
    ).delete()

    otp = str(random.randint(100000, 999999))
    expires = datetime.utcnow() + timedelta(minutes=5)

    verification = EmailVerification(
        email=email,
        student_id=student_id,
        name=name,
        password_hash=hash_password(password),
        otp=otp,
        expires_at=expires
    )

    db.add(verification)
    db.commit()

    send_email(email, otp)

    return {"message": "OTP sent to email"}

# ================== VERIFY OTP ==================

@app.post("/verify-otp")
def verify_otp(data: dict, db: Session = Depends(get_db)):

    email = data.get("email")
    otp = data.get("otp")

    if not email or not otp:
        raise HTTPException(status_code=400, detail="Missing email or otp")

    record = db.query(EmailVerification).filter(
        EmailVerification.email == email,
        EmailVerification.otp == otp
    ).first()

    if not record:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if record.expires_at < datetime.utcnow():
        db.delete(record)
        db.commit()
        raise HTTPException(status_code=400, detail="OTP expired")

    # สร้าง user จริง
    new_user = User(
        student_id=record.student_id,
        name=record.name,
        email=record.email,
        password_hash=record.password_hash,
        role="student"
    )

    db.add(new_user)
    db.delete(record)
    db.commit()

    return {"message": "Registration complete"}

# ================== LOGIN ==================

@app.post("/login")
def login(data: dict, db: Session = Depends(get_db)):

    student_id = data.get("student_id")
    password = data.get("password")

    if not student_id or not password:
        raise HTTPException(status_code=400, detail="Missing credentials")

    user = db.query(User).filter_by(student_id=student_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Wrong password")

    return {
        "id": user.id,
        "name": user.name,
        "role": user.role
    }

# ================== ROOT ==================

@app.get("/")
def root():
    return {"message": "OTP Email Verification Backend Running 🚀"}
