# app/models/message.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from app.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    room = Column(String, nullable=False, index=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Optional relationship to User
    # Only if you have User model and back_populates
    # user = relationship("User", back_populates="messages")


