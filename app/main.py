from fastapi import FastAPI
from app.api import auth, chat
from app.core.security import get_current_user
from fastapi import Depends
from sqlalchemy.orm import Session
from app.models.message import Message
from app.schemas import MessageOut
from app.database import Base, engine
from app.models import message

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()

app.include_router(auth.router)
app.include_router(chat.router)

# Test route
@app.get("/")
async def root():
    return {"message": "Real-time chat backend is starting!"}

# Protected route example
@app.get("/protected")
async def protected(user=Depends(get_current_user)):
    return {"user": user}

# Utility function to save message to the database

def save_message(db: Session, message: Message) -> MessageOut:
    db.add(message)
    db.commit()
    db.refresh(message)
    return MessageOut.from_orm(message)