from sqlalchemy import Column, Integer, String, Text,ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)

    chats = relationship("Chat", back_populates="conversation")
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

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="chats")

# ================== SKILL LEVEL ==================

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    level = Column(Integer, default=1)


# ================== DOCUMENT STORAGE ==================

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    uploaded_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)