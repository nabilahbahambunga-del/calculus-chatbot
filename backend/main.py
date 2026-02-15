from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Chat, Skill, Document, ExerciseResult
from auth import hash_password, verify_password
from ai import ask_llama, grade_answer
from pdf_utils import pdf_to_text
import shutil, os, json
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_admin(user):
    if user.role != "admin":
        raise HTTPException(status_code=403)

# ---------- AUTH ----------
@app.post("/register")
def register(data: dict, db: Session = Depends(get_db)):
    user = User(
        student_id=data["student_id"],
        name=data["name"],
        password_hash=hash_password(data["password"]),
        role="student"
    )
    db.add(user)
    db.commit()
    return {"message": "registered"}

@app.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(student_id=data["student_id"]).first()
    if not user or not verify_password(data["password"], user.password_hash):
        return {"error": "login failed"}
    return {"id": user.id, "name": user.name, "role": user.role}

# ---------- PDF ----------
@app.post("/upload_pdf")
def upload_pdf(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    require_admin(user)

    os.makedirs("uploads", exist_ok=True)
    path = f"uploads/{file.filename}"

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    text = pdf_to_text(path)
    db.add(Document(filename=file.filename, content=text))
    db.commit()

    return {"message": "PDF uploaded"}

# ---------- CHAT ----------
@app.post("/chat")
def chat(data: dict, db: Session = Depends(get_db)):

    user_id = data["user_id"]
    msg = data["message"]

    skill = db.query(Skill).filter_by(user_id=user_id).first()
    if not skill:
        skill = Skill(user_id=user_id, level=1)
        db.add(skill)
        db.commit()

    history = db.query(Chat).filter_by(user_id=user_id).all()
    formatted = [{"role": c.role, "content": c.content} for c in history]

    context = ""
    docs = db.query(Document).all()
    if docs:
        context = "\n".join(d.content[:1000] for d in docs)

    # ---------- AI Tutor ----------
    reply = ask_llama(
        formatted + [{"role": "user", "content": msg}],
        skill.level,
        context
    )

    # ---------- AI Grading ----------
    try:
        grade_json = grade_answer("คำถามล่าสุด", msg)
        grade_data = json.loads(grade_json)

        score = int(grade_data.get("score", 0))
        correct = bool(grade_data.get("correct", False))

    except:
        score = 0
        correct = False

    # ---------- Update Level ----------
    if correct:
        skill.level = min(skill.level + 1, 5)

    # ---------- Save ----------
    db.add(ExerciseResult(
        user_id=user_id,
        question=msg,
        correct=correct,
        score=score
    ))

    db.add(Chat(user_id=user_id, role="user", content=msg))
    db.add(Chat(user_id=user_id, role="assistant", content=reply))

    db.commit()

    return {
        "reply": reply,
        "score": score,
        "correct": correct,
        "level": skill.level
    }

# ---------- DASHBOARD ----------
@app.get("/admin/dashboard")
def dashboard(user_id: int, db: Session = Depends(get_db)):

    user = db.query(User).get(user_id)
    require_admin(user)

    total_users = db.query(User).filter(User.role == "student").count()
    total_chats = db.query(Chat).count()
    total_docs = db.query(Document).count()

    # ===== Daily Average =====
    results = db.query(ExerciseResult).all()

    daily_scores = {}
    for r in results:
        day = r.created_at.date()
        daily_scores.setdefault(day, []).append(r.score)

    daily_avg = [
        {"date": str(day), "avg_score": sum(scores)/len(scores)}
        for day, scores in daily_scores.items()
    ]

    # ===== Student Progress =====
    students = db.query(User).filter(User.role == "student").all()
    student_progress = []

    for s in students:
        user_results = db.query(ExerciseResult)\
            .filter_by(user_id=s.id)\
            .order_by(ExerciseResult.created_at)\
            .all()

        scores = [r.score for r in user_results]

        student_progress.append({
            "name": s.name,
            "scores": scores
        })

    return {
        "total_users": total_users,
        "total_chats": total_chats,
        "total_docs": total_docs,
        "daily_avg": daily_avg,
        "student_progress": student_progress
    }
