from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base


# ================== USERS ==================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    student_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # 🎓 เพิ่มใหม่
    year = Column(Integer, nullable=False)     # ชั้นปี 1-4
    major = Column(String, nullable=False)     # สาขาวิชา

    role = Column(String, default="student")
    is_verified = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ================== EXERCISE RESULTS ==================

class ExerciseResult(Base):
    __tablename__ = "exercise_results"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    question = Column(String)
    correct = Column(Boolean)
    score = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ================== CHAT HISTORY ==================

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    role = Column(String)      # user / assistant
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ================== SKILL LEVEL ==================

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    level = Column(Integer, default=1)


# ================== DOCUMENT STORAGE ==================

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    content = Column(Text)