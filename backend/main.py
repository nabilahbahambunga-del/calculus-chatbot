from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import shutil, os, json, random
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

from database import SessionLocal, engine
from models import Base, User, Chat, Skill, ExerciseResult, EmailVerification
from auth import hash_password, verify_password
from ai import ask_llama, grade_answer

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

    if not EMAIL_USER or not EMAIL_PASS:
        raise Exception("Email credentials not set")

    msg = MIMEText(f"Your verification code is: {otp}")
    msg["Subject"] = "Email Verification - AI Tutor"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.send_message(msg)
    server.quit()

# ================== SEND OTP ==================

@app.post("/send-otp")
def send_otp(data: dict, db: Session = Depends(get_db)):

    student_id = data.get("student_id")
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([student_id, name, email, password]):
        raise HTTPException(status_code=400, detail="Missing fields")

    existing = db.query(User).filter(
        (User.student_id == student_id) |
        (User.email == email)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

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

# ================== CHAT ==================

@app.post("/chat")
def chat(data: dict, db: Session = Depends(get_db)):

    user_id = data.get("user_id")
    message = data.get("message")

    if not user_id or not message:
        raise HTTPException(status_code=400, detail="Missing fields")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    skill = db.query(Skill).filter_by(user_id=user_id).first()
    if not skill:
        skill = Skill(user_id=user_id, level=1)
        db.add(skill)
        db.commit()

    history = db.query(Chat).filter_by(user_id=user_id).all()
    formatted = [{"role": c.role, "content": c.content} for c in history]

    reply = ask_llama(
        formatted + [{"role": "user", "content": message}],
        skill.level,
        ""
    )

    try:
        grade_json = grade_answer("question", message)
        grade_data = json.loads(grade_json)
        score = int(grade_data.get("score", 0))
        correct = bool(grade_data.get("correct", False))
    except:
        score = 0
        correct = False

    if correct:
        skill.level = min(skill.level + 1, 5)

    db.add(Chat(user_id=user_id, role="user", content=message))
    db.add(Chat(user_id=user_id, role="assistant", content=reply))

    db.add(ExerciseResult(
        user_id=user_id,
        question=message,
        correct=correct,
        score=score
    ))

    db.commit()

    return {
        "reply": reply,
        "score": score,
        "correct": correct,
        "level": skill.level
    }

# ================== ROOT ==================

@app.get("/")
def root():
    return {"message": "AI Tutor Backend Running 🚀"}