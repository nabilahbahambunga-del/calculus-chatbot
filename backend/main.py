from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
import os
from pdf_utils import pdf_to_text
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import re
from datetime import datetime
from database import SessionLocal, engine
from models import Base, User, Chat, Skill, ExerciseResult, Conversation
from auth import hash_password, verify_password
from ai import ask_llama

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
    pattern = r"^\d{10}@psu\.ac\.th$"
    if not re.match(pattern, email):
        raise HTTPException(
            status_code=400,
            detail="อีเมลต้องเป็น รหัสนักศึกษา@psu.ac.th"
        )

def validate_password(password: str):
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

    validate_psu_email(email)
    validate_password(password)

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

# ================== CREATE NEW CONVERSATION ==================

@app.post("/conversation/new")
def new_conversation(data: dict, db: Session = Depends(get_db)):

    user_id = data.get("user_id")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    convo = Conversation(
        user_id=user_id,
        title="New Chat",
        created_at=datetime.utcnow()
    )

    db.add(convo)
    db.commit()
    db.refresh(convo)

    return {"conversation_id": convo.id}

# ================== GET USER CONVERSATIONS ==================

@app.get("/conversations")
def get_conversations(user_id: int, db: Session = Depends(get_db)):

    convos = db.query(Conversation).filter_by(user_id=user_id).order_by(
        Conversation.created_at.desc()
    ).all()

    return [
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at
        }
        for c in convos
    ]

# ================== GET MESSAGES IN CONVERSATION ==================

@app.get("/conversation/messages")
def get_messages(conversation_id: int, user_id: int, db: Session = Depends(get_db)):

    convo = db.query(Conversation).filter_by(
        id=conversation_id,
        user_id=user_id
    ).first()

    if not convo:
        raise HTTPException(status_code=403, detail="Access denied")

    messages = db.query(Chat).filter_by(
        conversation_id=conversation_id
    ).order_by(Chat.created_at).all()

    return [
        {"role": m.role, "content": m.content}
        for m in messages
    ]

# ================== CHAT ==================

@app.post("/chat")
def chat(data: dict, db: Session = Depends(get_db)):

    user_id = data.get("user_id")
    message = data.get("message")
    conversation_id = data.get("conversation_id")

    if not all([user_id, message, conversation_id]):
        raise HTTPException(status_code=400, detail="Missing data")

    convo = db.query(Conversation).filter_by(
        id=conversation_id,
        user_id=user_id
    ).first()

    if not convo:
        raise HTTPException(status_code=403, detail="Invalid conversation")

    history = db.query(Chat).filter_by(
        conversation_id=conversation_id
    ).order_by(Chat.created_at).all()

    formatted = [{"role": c.role, "content": c.content} for c in history]

    reply = ask_llama(
        formatted + [{"role": "user", "content": message}],
        1,
        ""
    )

    db.add(Chat(
        user_id=user_id,
        conversation_id=conversation_id,
        role="user",
        content=message,
        created_at=datetime.utcnow()
    ))

    db.add(Chat(
        user_id=user_id,
        conversation_id=conversation_id,
        role="assistant",
        content=reply,
        created_at=datetime.utcnow()
    ))

    db.commit()

    return {"reply": reply}

# ================== ADMIN DASHBOARD ==================

@app.get("/admin/dashboard")
def admin_dashboard(user_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access only")

    results = db.query(ExerciseResult).all()

    daily = {}
    for r in results:
        if not r.created_at:
            continue

        date = r.created_at.date()

        if date not in daily:
            daily[date] = []

        daily[date].append(r.score)

    daily_avg = [
        {"date": str(d), "avg_score": sum(scores)/len(scores)}
        for d, scores in daily.items()
    ]

    students = db.query(User).all()
    student_progress = []

    for s in students:
        scores = db.query(ExerciseResult).filter_by(user_id=s.id).all()
        student_progress.append({
            "name": s.name,
            "scores": [x.score for x in scores]
        })

    return {
        "daily_avg": daily_avg,
        "student_progress": student_progress
    }

# ================== UPLOAD PDF ==================

from fastapi import Form

@app.post("/upload_pdf")
async def upload_pdf(
    user_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    text = pdf_to_text(file_path)

    return {
        "message": "Upload successful",
        "filename": file.filename
    }
# ================== ROOT ==================

@app.get("/")
def root():
    return {"message": "PSU AI Tutor Backend Running 🚀"}