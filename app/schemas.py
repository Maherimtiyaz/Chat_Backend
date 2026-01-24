from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    room : str
    content: str

# Response model for messages    

class MessageOut(BaseModel):
    id: int
    room: str
    user_id: int
    username: str
    content: str
    created_at: datetime

# ORM mode to work with SQLAlchemy models

    class Config:
        orm_mode = True