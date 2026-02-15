from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from datetime import datetime
from database import Base
from sqlalchemy.sql import func
from sqlalchemy import DateTime

class ExerciseResult(Base):
    __tablename__ = "exercise_results"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    question = Column(String)
    correct = Column(Boolean)
    score = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    student_id = Column(String, unique=True)
    name = Column(String)
    password_hash = Column(String)
    role = Column(String, default="student")

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    role = Column(String)
    content = Column(Text)

class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    level = Column(Integer, default=1)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    content = Column(Text)
