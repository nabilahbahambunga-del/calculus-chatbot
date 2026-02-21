from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import re
import json

from database import SessionLocal, engine
from models import Base, User, Chat, Skill, ExerciseResult
from auth import hash_password, verify_password
from ai import ask_llama, grade_answer

# ================== INIT ==================

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

# ================== VALIDATION ==================

def validate_psu_email(email: str):
    """
    ต้องเป็น:
    - รหัสนักศึกษา
    - ตามด้วย @psu.ac.th
    """
    pattern = r"^\d{10}@psu\.ac\.th$"
    if not re.match(pattern, email):
        raise HTTPException(
            status_code=400,
            detail="อีเมลต้องเป็น รหัสนักศึกษา@psu.ac.th"
        )

def validate_password(password: str):
    """
    รหัสผ่านต้อง:
    - ยาวอย่างน้อย 6 ตัว
    - มีตัวอักษรอย่างน้อย 1 ตัว
    """
    if len(password) < 6:
        raise HTTPException(
            status_code=400,
            detail="รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร"
        )

    if not re.search(r"[A-Za-z]", password):
        raise HTTPException(
            status_code=400,
            detail="รหัสผ่านต้องมีตัวอักษรอย่างน้อย 1 ตัว"
        )

# ================== REGISTER ==================

@app.post("/register")
def register(data: dict, db: Session = Depends(get_db)):

    student_id = data.get("student_id")
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([student_id, name, email, password]):
        raise HTTPException(status_code=400, detail="Missing fields")

    # 🔐 ตรวจสอบ email format
    validate_psu_email(email)

    # 🔐 ตรวจสอบ password
    validate_password(password)

    # 🔍 เช็คว่ามี user ซ้ำไหม
    existing = db.query(User).filter(
        (User.student_id == student_id) |
        (User.email == email)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        student_id=student_id,
        name=name,
        email=email,
        password_hash=hash_password(password),
        role="student"
    )

    db.add(new_user)
    db.commit()

    return {"message": "Registration successful"}

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

@app.get("/admin/dashboard")
def admin_dashboard(user_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()

    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

# ================== ROOT ==================

@app.get("/")
def root():
    return {"message": "PSU AI Tutor Backend Running 🚀"}